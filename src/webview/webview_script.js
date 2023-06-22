const vscode = acquireVsCodeApi();
var STEP_FACTOR = 5;


function checkCollision(div1, div2) {
    // Get the bounding rectangles of the div elements
    if (!div1 || !div2) { return null; }
    const rect1 = div1.getBoundingClientRect();
    const rect2 = div2.getBoundingClientRect();

    // Check for collision
    if (rect1.right < rect2.left || rect1.left > rect2.right) {
        return null;
    }

    return [div1.id, div2.id, Math.max(0, Math.min(rect1.right, rect2.right) - Math.max(rect1.left, rect2.left))];
}

function getProportions(div) {
    const id = div.id;
    const value = id.split("-").pop();
    const parent = div.parentElement.id.split("-");
    if (!parent.includes("max")) { return; }
    const max = parent[parent.indexOf("max") + 1];
    const min = parent[parent.indexOf("min") + 1];
    return [min, value, max];
}

function removeHighlight() {
    document.querySelectorAll(".highlight").forEach((e) => {
        e.classList.remove("highlight");
    });

    document.querySelectorAll(".column-highlight").forEach((e) => {
        e.remove();
    });
}

function notifyHighlight(entry) {
    vscode.postMessage({
        command: "highlight-line",
        id: entry.parentElement.id
    });
}

function highlightLine(entry) {

    removeHighlight();

    entry.parentElement.classList.add("highlight");
    const entryWidth = entry.offsetWidth;

    column_highlight = document.createElement("div");
    column_highlight.classList.add("highlight", "column-highlight");

    column_highlight.style.width = entryWidth + "px";
    column_highlight.style.height = document.getElementsByClassName("lineWrapper")[0].offsetHeight + "px";
    column_highlight.style.left = entry.getBoundingClientRect().left - document.body.getBoundingClientRect().left + "px";

    document.body.insertBefore(column_highlight, document.body.firstChild);

    notifyHighlight(entry);

    // document.querySelectorAll(".column-width").forEach((e) => {
    //     e.style.width = entry_width + 30 + "px";
    //     e.style.maxWidth = entry_width + 30 + "px";
    // });
}

function findColisionInline(line) {
    const lineEntries = line.children;
    const colisions = [];
    for (var number = 0; number < lineEntries.length; number++) {
        const colision = checkCollision(lineEntries[number], lineEntries[number + 1]);
        if (colision) {
            colisions.push(colision);
        }
    }
    return colisions;
}

function findAllColisions() {
    const lineWrappers = document.querySelectorAll(".lineWrapper")[0];
    const collisions = [];
    const children = lineWrappers.children;
    for (var number = 0; number < children.length; number++) {
        collisions.push(...findColisionInline(children[number]));
    }
    return collisions;
}

function changeBarToText(div) {
    const originalWidth = div.parentElement.classList[1].split("-").pop();
    div.style.width = originalWidth + "px";
    div.style.maxWidth = originalWidth + "px";
    div.innerHTML = div.id.split("-").pop();
}

function removeAllBars() {
    document.querySelectorAll(".bar").forEach((e) => {
        changeBarToText(e.parentElement);
    });
}


function changeDivToBar(div, overlap) {
    const oldWidth = div.offsetWidth;
    div.style.width = oldWidth - overlap + "px";

    const proportions = getProportions(div);
    const min = proportions[0];
    const value = proportions[1];
    const max = proportions[2];

    if (max === min) { return; } // only one constant value

    var barHeight = null;
    var barTop = null;


    if (min <= 0 && max <= 0) { // only negative values
        barHeight = (max - value) / (max - min) * 100;
        barTop = 0;
    } else if (min >= 0 && max >= 0) { // only positive values
        barHeight = 100;
        barTop = (max - value) / (max - min) * 100;
    } else if (value >= 0) { // positive value between negative and positve values
        barHeight = (max - value) / (max - min) * 100;
        barHeight += (0 - min) / (max - min) * 100;
        barHeight = 1 - barHeight;
        barTop = (max - value) / (max - min) * 100;
    } else if (value <= 0) { // negative value between negative and positve values
        barTop = (max - 0) / (max - min) * 100;
        barHeight = (value - min) / (max - min) * 100;
        barHeight = 1 - (barHeight + barTop);
    }
    barTop = barTop === 100 ? 99 : barTop;
    console.log(min, value, max);
    console.log(barHeight, barTop);
    div.innerHTML = "<div class='bar' style='height: " + barHeight + "%; top: " + barTop + "%;'></div>";

}


function handleColisions() {
    const collisions = findAllColisions();
    const colisionMap = getColisionMap(collisions);
    console.log(colisionMap);
    for (var key in colisionMap) {
        changeDivToBar(document.getElementById(key), colisionMap[key]);
    }

}

function getColisionMap(collisions) {
    var colisionMap = new Map();
    for (var number = 0; number < collisions.length; number++) {

        if (colisionMap[collisions[number][0]]) {
            colisionMap[collisions[number][0]].push(collisions[number][2]);
        } else {
            colisionMap[collisions[number][0]] = [collisions[number][2]];
        }

        if (colisionMap[collisions[number][1]]) {
            colisionMap[collisions[number][1]].push(collisions[number][2]);
        } else {
            colisionMap[collisions[number][1]] = [collisions[number][2]];
        }
    }

    for (var key in colisionMap) {
        var value = colisionMap[key];
        const len = value.length;
        value = value.reduce(function (a, b) { return a + b; }) / len;
        colisionMap[key] = value;
    }

    return colisionMap;
}

// https://stackoverflow.com/a/21015393
function getTextWidth(text, font) {
    const canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
    const context = canvas.getContext("2d");
    context.font = font;
    return context.measureText(text).width;
}

function getCssStyle(element, prop) {
    return window.getComputedStyle(element, null).getPropertyValue(prop);
}

function getCanvasFont(el) {
    const fontWeight = getCssStyle(el, 'font-weight') || 'normal';
    const fontSize = getCssStyle(el, 'font-size') || '16px';
    const fontFamily = getCssStyle(el, 'font-family') || 'Times New Roman';

    return `${fontWeight} ${fontSize} ${fontFamily}`;
}

function getMaxEntryWidth(line, font) {
    var maxWidth = 0;
    const entries = line.children;
    for (const entry of entries) {
        const width = getTextWidth(entry.innerHTML, font);
        if (width > maxWidth) {
            maxWidth = width;
        }
    }
    return Math.ceil(maxWidth);
}

function initWidths() {
    const entry = document.querySelectorAll(".entry")[0];
    const font = getCanvasFont(entry);
    const lines = document.querySelectorAll(".lineWrapper")[0].children;
    for (const line of lines) {
        const width = getMaxEntryWidth(line, font);
        line.classList.add("max-width-" + width);
        const entries = line.children;
        for (const entry of entries) {
            entry.style.width = width + "px";
            entry.style.maxWidth = width + "px";
        }
    }
}





document.querySelectorAll(".entry").forEach((e) => {
    e.addEventListener("click", highlightLine.bind(null, e));
});

// initialize width for all entries
initWidths();
handleColisions();



