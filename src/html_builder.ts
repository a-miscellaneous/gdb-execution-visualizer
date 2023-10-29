import * as interfaces from "./interfaces";
import * as fs from 'fs';
import * as utils from "./utils";


var OFFSET_FACTOR = 5;


export function getPureHTML(historyPath: string): interfaces.FileToHTML {
    const obj = getOBJfromJSON(historyPath);
    const fileToHTML = getHTMLfromOBJ(obj);
    return fileToHTML;

}


function getOBJfromJSON(path: string): interfaces.ExeHistory {
    const data = fs.readFileSync(path, { encoding: 'utf8', flag: 'r' });
    const obj: interfaces.ExeHistory = JSON.parse(data);
    return obj;
}


function getHTMLfromOBJ(lineHistorys: interfaces.ExeHistory): interfaces.FileToHTML {
    // for each file
    return utils.objMap(lineHistorys, (value: interfaces.LineMapping) => {
        return getHTMLperLine(value);
    });
}


function getHTMLperLine(lineHistory: interfaces.LineMapping): string[] {
    // for each line
    const newObj = utils.objMap(lineHistory, (value: interfaces.LineHistory | interfaces.ArgsHistory, key: string) => {
        if ("functionName" in value) {
            return `<div class="line editor-height" id="line-${key}">${getHTMLperArgsHistory(value)}</div>`;
        } else {
            return `<div class="line editor-height" id="line-${key}-max-${value.maxValue}-min-${value.minValue}">${getHTMLperLineHistory(value)}</div>`;
        }
    });

    // 0 padding
    const maxLine = Math.max(...Object.keys(newObj).map(Number));
    for (let i = 0; i < maxLine; i++) {
        if (!newObj[i]) {
            newObj[i] = `<div class="line editor-height" id="line-${i}" ></div>`;
        }
    }

    return Object.values(newObj);
}


function getHTMLperArgsHistory(argsHistory: interfaces.ArgsHistory): string {
    return `<div class="entry column-width editor-height" id="name-${argsHistory.functionName}"> arg</div>`;
}

function getHTMLperLineHistory(lineHistory: interfaces.LineHistory): string {
    const lineHistoryValues = lineHistory.values;
    const lineHistoryValuesHTML = lineHistoryValues.map((value: interfaces.LineHistoryValues) => {
        return `<div class="entry column-width editor-height" id="step-${value.step}-value-${value.value}" style="left: ${value.step * OFFSET_FACTOR}px">${value.value}</div>`;
    });
    return lineHistoryValuesHTML.join("");
}

