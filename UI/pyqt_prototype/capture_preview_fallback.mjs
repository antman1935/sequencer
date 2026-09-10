import sharp from 'sharp';
import { resolve } from 'node:path';

const svgPath = resolve('preview.svg');
const screenshotPath = resolve('preview.png');

await sharp(svgPath).png().toFile(screenshotPath);
console.log(screenshotPath);
