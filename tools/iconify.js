#!/usr/bin/env node
const {Jimp} = require("jimp");
const { intToRGBA } = require("@jimp/utils");
const {cd, ls} = require('shelljs');
const {parse} = require("path");

const data={};
const files = ls('./*.png');


(async function() {
    for (const file of files) {
        const id = parse(file).name

        const img = await Jimp.read(file);

        const width = img.width;
        const height = img.height;

        const datum = data[file] = {
            pal: [],
            pixels: new Array(width*height)
        }

        let icon = `${id}=`
        for (let y=0; y<height; y++) {
            for (let x=0; x<width; x++) {
                const rgba = intToRGBA(img.getPixelColor(x, y))

                icon += (rgba.r < 128 ? 0 : 1).toString();
            }
        }
        console.log(icon)
    }
})();
