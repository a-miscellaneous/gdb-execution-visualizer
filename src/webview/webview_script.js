const MAX_WIDTH = 15;
var currentWidth = 20;


function checkCollision(div1, div2) {
    // Get the bounding rectangles of the div elements
    const rect1 = div1.getBoundingClientRect();
    const rect2 = div2.getBoundingClientRect();

    // Check for collision
    if (rect1.right < rect2.left || rect1.left > rect2.right) {
        return null;
    }
    return Math.max(0, Math.min(rect1.right, rect2.right) - Math.max(rect1.left, rect2.left));
}

function getProportions(div) {
    const id = div.id;
    const value = id.split("-").pop();
    const parent = div.parentElement.id.split("-");
    if (!parent.includes("max")) { return; }
    const max = parent[parent.indexOf("max") + 1];
    const min = parent[parent.indexOf("min") + 1];
    return (min, value, max);
}

function removeHighlight() {
    document.querySelectorAll(".highlight").forEach((e) => {
        e.classList.remove("highlight");
    });

    document.querySelectorAll(".column-highlight").forEach((e) => {
        e.remove();
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
    column_highlight.style.left = entry.offsetLeft + entryWidth + "px";

    document.body.insertBefore(column_highlight, document.body.firstChild);

    // document.querySelectorAll(".column-width").forEach((e) => {
    //     e.style.width = entry_width + 30 + "px";
    //     e.style.maxWidth = entry_width + 30 + "px";
    // });
}



document.querySelectorAll(".entry").forEach((e) => {
    e.addEventListener("click", highlightLine.bind(null, e));
});


