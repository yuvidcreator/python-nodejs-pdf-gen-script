// optimizedFonts.js
import fs from 'fs';

function loadFont(filePath) {
    return fs.readFileSync(filePath).toString('base64');
}

const fonts = {
    montserratBlack: loadFont('./public/fonts/MontserratAlternates-Black.woff'),
    montserratBold: loadFont('public/fonts/MontserratAlternates-Bold.woff'),
    notoKR: loadFont('./public/fonts/NotoSansKR-VariableFont_wght.woff2'),
    notoSansCJKkrBold: loadFont('./public/fonts/NotoSansCJKkrBold.woff2'),
    notoCJKKRMedium: loadFont('./public/fonts/NotoSansCJKkrMedium.woff2'),
    notoCJKKRRegular: loadFont('./public/fonts/NotoSansCJKkrRegular.ttf'),
    notosansCJKscRegular: loadFont('./public/fonts/NotoSansCJKscRegular.woff2'),
    notoSansCJKkrLight: loadFont('./public/fonts/NotoSansCJKkrLight.woff2'),
    notoSansCJKjpBold: loadFont('./public/fonts/NotoSansCJKjp-Bold.ttf'),
    notoSansCJKjpVF: loadFont('./public/fonts/NotoSansCJKjp-VF.woff2'),
    georgia: loadFont('./public/fonts/georgia.ttf')
};


const myCustomFonts = `
    @font-face {
        font-family: 'MontserratAlternates-Black';
        src: url(data:font/woff;base64,${fonts.montserratBlack}) format('woff');
        font-style: normal;
        font-weight: 900;
    }
    @font-face {
        font-family: 'MontserratAlternates-Bold';
        src: url(data:font/woff;base64,${fonts.montserratBold}) format('woff');
        font-style: normal;
        font-weight: 900;
    }
    @font-face {
        font-family: 'Noto Sans KR';
        src: url(data:font/woff2;base64,${fonts.notoKR}) format('woff2');
    }
    @font-face {
        font-family: 'NotoSansCJKkrBold';
        src: url(data:font/woff2;base64,${fonts.notoSansCJKkrBold}) format('woff2');
        font-display: block;
    }
    @font-face {
        font-family: 'NotoSansCJKkrMedium';
        src: url(data:font/woff2;base64,${fonts.notoCJKKRMedium}) format('woff2');
        font-display: block;
    }
    @font-face {
        font-family: 'NotoSansCJKkrRegular';
        src: url(data:font/ttf;base64,${fonts.notoCJKKRRegular}) format('ttf');
        font-display: block;
    }
    @font-face {
        font-family: 'notosanscjkscregular';
        src: url(data:font/woff2;base64,${fonts.notosansCJKscRegular}) format('woff2');
        font-display: block;
    }
    @font-face {
        font-family: 'NotoSansCJKkrLight';
        src: url(data:font/woff2;base64,${fonts.notoSansCJKkrLight}) format('woff2');
        font-display: block;
    }
    @font-face {
        font-family: 'NotoSansCJKjp-Bold';
        src: url(data:font/ttf;base64,${fonts.notoSansCJKjpBold}) format('ttf');
        font-display: block;
    }
    @font-face {
        font-family: 'NotoSansCJKjp';
        src: url(data:font/woff2;base64,${fonts.notoSansCJKjpVF}) format('woff2');
        font-display: block;
    }
    @font-face {
        font-family: 'Georgia';
        font-weight: normal;
        src: url(data:font/ttf;base64,${fonts.georgia}) format('ttf');
        font-display: block;
    }
`;

export default myCustomFonts;
