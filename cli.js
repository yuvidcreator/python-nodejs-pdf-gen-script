#!/usr/bin/env node

import { generatePdf } from './pdfGenerate.js';
import path from 'path';
import { performance } from 'perf_hooks';

class CLIHandler {
    constructor() {
        this.startTime = performance.now();
    }

    async generatePDFCli(jsonData, outputPath) {
        try {
            console.log('🚀 Starting PDF generation...');
            console.log(`📄 Output: ${outputPath}`);
            
            const result = await generatePdf({ 
                data: jsonData, 
                outputPath: path.resolve(outputPath)
            });
            
            const duration = performance.now() - this.startTime;
            console.log(`⏱️  Total time: ${duration.toFixed(2)}ms`);
            
            return result;
            
        } catch (error) {
            console.error('❌ PDF generation failed:', error.message);
            throw error;
        }
    }

    async run() {
        try {
            const args = process.argv.slice(2);

            const dataArgIndex = args.indexOf('--data');
            const outputArgIndex = args.indexOf('--output');

            if (dataArgIndex === -1 || outputArgIndex === -1) {
                throw new Error('Invalid arguments. Provide --data and --output.');
            }
            
            // Parse JSON data
            const jsonData =  JSON.parse(args[dataArgIndex + 1]);
            const outputPath = args[outputArgIndex + 1];
            
            // Generate PDF
            await this.generatePDFCli(jsonData, outputPath);
            
            console.log('✅ PDF generation completed successfully!');
            process.exit(0);
            
        } catch (error) {
            console.error('❌ Error:', error.message);
            
            if (error.message.includes('Invalid arguments')) {
                console.log('\nUse --help for usage information.');
            }
            
            process.exit(1);
        }
    }
}

// Handle unhandled rejections
process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught Exception:', error);
    process.exit(1);
});

// Run CLI
const cli = new CLIHandler();
cli.run();