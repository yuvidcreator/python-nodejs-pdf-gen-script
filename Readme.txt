## Testing Python + NodeJS script PDF Generation script ##

# Auto-subset fonts based on real HTML usage via glyphhanger
# globally for CLI usage
npm install -g glyphhanger 

# Then install node modules using npm / yarn
npm install 
or
yarn install

# Then create python env / venv environment using below command and 
# install packages listed in requirements.txt
python3 -m venv env
source env/bin/activate
pip install -U pip 
pip install -r requirements.txt

# Then first of all optimize fonts -- run below commnad
node build-fonts.js
or
build:fonts

-- All operations are in-memory
-- Injecting custom templates/fonts/css-styles/static-images
-- Dynamic data injection from .json file
-- Dynamic ploted graphs rendering using base64


# Project structure -->
pdf_generator_cli/
├── cli.js
├── customFonts.js
├── customStyles.js
├── htmlTemplates.js (Optinal)
├── pdfGenerator.js
├── run_pdfgen.py
└── templates/
|    └── page1.ejs 
|    └── page2.ejs
└── public/
|   └── css/
|   └── fonts/
|   └── images/
└── output/
    └── final.pdf   ✅ Only file written to disk


# Setup Guide -->
1. Install Node.js Packages:
npm init -y
npm install puppeteer ejs pdf-lib

2. Install Python Requirements:
pip install matplotlib

3. Run It:
python run_pdfgen.py

Optional Cleanup (Commented) :
1. Python:
os.remove(output_path)  # after sending email/upload

2. Node.js:
fs.unlinkSync(outputPath);




@font-face {
    font-family: 'OpenSans';
    src: url(data:font/ttf;base64,<%= embeddedFonts.OpenSans %>) format('truetype');
}
@font-face {
    font-family: 'Roboto-Bold';
    src: url(data:font/ttf;base64,<%= embeddedFonts.RobotoBold %>) format('truetype');
}
@font-face {
    font-family: 'Montserrat Alternates Black';
    src: url(data:font/ttf;base64,<%= embeddedFonts.MontserratAlternatesBlack %>) format('woff');
}



@font-face {
    font-family: 'OpenSans';
    src: url(data:font/ttf;base64,<%= embeddedFonts.OpenSans %>) format('truetype');
}
@font-face {
    font-family: 'Roboto-Bold';
    src: url(data:font/ttf;base64,<%= embeddedFonts.RobotoBold %>) format('truetype');
}
@font-face {
    font-family: 'Montserrat Alternates Black';
    src: url(data:font/ttf;base64,<%= embeddedFonts.MontserratAlternatesBlack %>) format('woff');
}
@font-face {
    font-family: 'Rambla';
    src: url(data:font/ttf;base64,<%= embeddedFonts.RamblaReg %>) format('woff');
}

<link rel="preload" as="font" href="/fonts/NotoSansCJKjp-VF.woff2" type="font/woff2" crossorigin="anonymous">
@font-face {
    font-family: 'NotoSansCJKjp';
    src: url('/fonts/NotoSansCJKjp-VF.woff2') format('woff2'),
        url('/fonts/NotoSansCJKjp-VF.woff') format('woff');
    font-style: normal;
    font-display: swap;
}
<%- include('partials/customFonts.ejs') %>


# Base64 image rendering .ejs template -- example
-- for svg code :
<img src="data:image/svg+xml;base64,<%= RadarGraphBase64 %>"  width="391" height="361" class="img-fluid mx-auto d-block"/>

-- for webp/png/jpg file path :
<img src="<%= RadarGraphBase64 %>" alt="Polar Radar Chart Image"  class="webp-chart" />