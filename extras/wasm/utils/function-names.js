const fs = require('fs');
const xpath = require('xpath');
const { DOMParser } = require('xmldom');

const inputXmlFilename = process.argv[2];
const extraFunctions = process.argv[3] ? process.argv[3].split(',') : [];
const inputXmlContent = fs.readFileSync(inputXmlFilename, 'utf-8');
const inputDom = new DOMParser().parseFromString(inputXmlContent);
const nodes = xpath.select('//member[@kind="function"]/name/text()', inputDom);

const allFunctions = [...nodes.map(node => node.toString()), ...extraFunctions];

console.log(
  JSON.stringify(allFunctions.map(functionName => '_' + functionName))
);
