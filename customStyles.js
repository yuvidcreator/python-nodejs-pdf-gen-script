const customCSS = `
@page {
    size: A4; /* Set page size to A4 */
    margin: 0mm; /* Adjust margin to fit content */
}
body {
    font-family: 'Noto Sans KR', sans-serif;
    margin: 0 auto;
    padding: 0;
    color: #333;
    background-color: #fff;
}
.container {
    width: 100%;
    display: flex;
    justify-content: center;
    min-height: 100vh;
}
.side-div {
    flex: 0 1 0; /* Takes 15% of the width, but not less than 15% */
}
.middle-div {
    flex: 1; /* Takes remaining space (3/4) */
    flex-direction: column;
    flex-flow: wrap;
    align-items: center;
}
footer {
    position: relative;
    /* height: 400px; */
    margin-top: 180px;
}
hr {
    border: none;
    height: 1px;
    width: 84%;
    /* Set the hr color */
    color: #d9d9d9;  /* old IE */
    background-color: #d9d9d9;  /* Modern Browsers */
}
`;
export default customCSS;
