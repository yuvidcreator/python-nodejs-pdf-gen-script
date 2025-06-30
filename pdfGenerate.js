// optimized_newPdfGen.js
import path from 'path';
import { promises as fs } from 'fs';
import fsSync from 'fs';
import ejs from 'ejs'
import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
// import { pdfgenConfig } from './pdfgen.config.js';
import customCSS from './customStyles.js';
// import { customFonts } from './templates/partials/customFonts.js';
import myCustomFonts from './customFonts.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

class OptimizedPDFGenerator {
    constructor() {
        this.browser = null;
        this.templates = new Map();
        this.staticAssets = new Map();
        this.isInitialized = false;
    }

    async initialize() {
        if (this.isInitialized) return;

        console.log('🚀 Initializing PDF Generator...');

        this.browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-background-networking',
                '--disable-sync',
                '--disable-translate',
                '--hide-scrollbars',
                '--metrics-recording-only',
                '--mute-audio',
                '--no-default-browser-check',
                '--no-zygote',
                '--single-process'
            ],
            defaultViewport: { width: 794, height: 1123 },
        });

        await Promise.all([
            this.preloadTemplates(),
            // this.getSortedEJSTemplates(),
            this.preloadStaticAssets()
        ]);

        this.isInitialized = true;
        console.log('✅ PDF Generator initialized');
    }

    async preloadTemplates() {
        const templatesDir = path.resolve('./templates');
        const files = await fs.readdir(templatesDir);
        const ejsFiles = files.filter(
            f => f.endsWith('.ejs')).sort(
            (a, b) => parseInt(a.match(/\d+/)?.[0] || '0') - parseInt(b.match(/\d+/)?.[0] || '0')
        );

        // const GLOBAL_INCLUDES = pdfgenConfig.globalIncludes.map(
        //     include => `<%- include('${include}') %>`
        // ).join('\n') + '\n';

        await Promise.all(ejsFiles.map(async (file) => {
            const fullPath = path.join(templatesDir, file);
            const content = await fs.readFile(fullPath, 'utf-8');
            
            // Inject includes if not already present
            // const alreadyHasAllIncludes = pdfgenConfig.globalIncludes.every(includePath =>
            //     content.includes(includePath)
            // );

            // if (!alreadyHasAllIncludes) {
            //     content = GLOBAL_INCLUDES + content;
            // }
            
            // ⬇️ IMPORTANT: Pass filename so EJS can resolve relative includes
            const compiled = ejs.compile(content, {
                async: true,
                filename: fullPath     // So includes resolve correctly
            });

            this.templates.set(file, { content, compiled });
        }));
        console.log(`📄 Loaded ${ejsFiles.length} templates`);
    }

    async preloadStaticAssets() {
        const assetsToLoad = [
            { key: 'staticBackground', path: './public/images/Conventional.png' }
        ];

        await Promise.all(assetsToLoad.map(async ({ key, path: assetPath }) => {
            if (fsSync.existsSync(assetPath)) {
                const buffer = await fs.readFile(assetPath);
                this.staticAssets.set(key, buffer.toString('base64'));
            } else {
                console.warn(`⚠️  Missing asset: ${assetPath}`);
            }
        }));
    }

    async getSortedEJSTemplates() {
        const templatesDir = path.resolve('./templates');
        const files = await fs.readdir(templatesDir);

        const ejsFiles = files
            .filter(f => f.endsWith('.ejs') && /^page\d+\.ejs$/.test(f))  // Only pageN.ejs
            .map(f => ({
            name: f,
            num: parseInt(f.match(/\d+/)[0])
            }))
            .sort((a, b) => a.num - b.num)
            .map(obj => obj.name);  // Return just the names

        await Promise.all(ejsFiles.map(async (file) => {
            const fullPath = path.join(templatesDir, file);
            const content = await fs.readFile(fullPath, 'utf-8');
            
            const compiled = ejs.compile(content, {
                async: true,
                filename: fullPath     // So includes resolve correctly
            });

            this.templates.set(file, { content, compiled });
        }));
        console.log(`📄 Loaded ${ejsFiles.length} templates`);

        return ejsFiles;
    }

    async renderTemplate(templateFile, data) {
        const template = this.templates.get(templateFile);
        if (!template) throw new Error(`Template not found: ${templateFile}`);

        const renderData = {
            ...data,
            customFonts: myCustomFonts,
            customCSS: customCSS,
            // staticBackground: this.staticAssets.get('staticBackground') || '',
        };

        return await template.compiled(renderData);
    }

    async generatePagePDF(html) {
        const page = await this.browser.newPage();

        // Set these options before loading your page
        await page.setCacheEnabled(true);
        await page.setRequestInterception(true);

        try {
            await page.setContent(html, {
                waitUntil: ['networkidle0', 'domcontentloaded'],
                timeout: 15000
            });

            await Promise.race([
                page.evaluateHandle('document.fonts.ready'),
                new Promise(res => setTimeout(res, 3000))
            ]);

            return await page.pdf({
                format: 'A4',
                printBackground: true,
                margin: { top: 0, right: 0, bottom: 0, left: 0 },
                preferCSSPageSize: true
            });
        } finally {
            await page.close();
        }
    }

    async generatePdf({ data, outputPath }) {
        await this.initialize();

        // // Auto detecting .ejs templates in templates dir
        // const pages = Array.from(this.templates.keys());

        // Manually listed .ejs templates
        // const orderedTemplateList = [
        //     'page1.ejs',
        //     'page2.ejs',
        //     'page3.ejs'
        // ];

        // Dynamically Build List If Count Known in ./templates/*.ejs files
        const pageCount = 10;
        const orderedTemplateList = Array.from({ length: pageCount }, (_, i) => `page${i + 1}.ejs`);

        const buffers = [];

        // for (const pageFile of pages) {
        for (const pageFile of orderedTemplateList) {
            const html = await this.renderTemplate(pageFile, data);
            const buffer = await this.generatePagePDF(html);
            buffers.push(buffer);
        }

        const pdfLib = await import('pdf-lib');
        const { PDFDocument } = pdfLib;
        const mergedPdf = await PDFDocument.create();

        for (const buffer of buffers) {
            const pdf = await PDFDocument.load(buffer);
            const copiedPages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
            copiedPages.forEach(p => mergedPdf.addPage(p));
        }

        const finalPdf = await mergedPdf.save();
        await fs.writeFile(outputPath, finalPdf);

        return outputPath;
    }
}

const generator = new OptimizedPDFGenerator();
export const generatePdf = (params) => generator.generatePdf(params);
