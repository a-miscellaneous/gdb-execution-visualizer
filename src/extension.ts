import * as vscode from "vscode";
import * as fs from "fs";
import * as interfaces from "./interfaces";
import * as utils from "./utils";
import * as path from "path";




export function activate(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand( "extension.showHistory",  () => {

        const panel = createWebViewPanel();
        const lineHeight = getLineHeight();
        const currentFile = getActiveDocument();
        console.log("Line Height:", lineHeight);
        console.log("Current File:", currentFile);


        const root = vscode.workspace.workspaceFolders;
        if (!root) {return;}
        const script = vscode.Uri.file(path.join(context.extensionPath, "src", "script.js"));

        const filePath = path.join(root[0].uri.fsPath, ".vscode", "history.json");
        const lineHistorys : interfaces.ExeHistory = getLineHistorys(filePath);
        const lineHistorysHTML : interfaces.FileToHTML = getHTMLperFile(lineHistorys);


        const htmlContent = lineHistorysHTML[path.parse(currentFile).base].join("");

        // Set the webview's HTML content
        setHTMLcontent(panel, htmlContent, lineHeight);

    });

    context.subscriptions.push(disposable);
}

function setHTMLcontent(panel: vscode.WebviewPanel, htmlContent: string, lineHeight: number) {
    const css = getCSS(lineHeight);
    const script = getScript();
    panel.webview.html = `
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>History</title>
                    ${css}
                </head>
                <body>
                    <div class="lineWrapper">
                    ${htmlContent}
                    </div>
                    ${script}
                </body>
            </html>
        `;
    console.log("HTML Content:", panel.webview.html);
}

function createWebViewPanel() {
    return vscode.window.createWebviewPanel(
        "historyWebView", // id
        "History", //title
        vscode.ViewColumn.Beside, //spawn location
        {   // Enable JavaScript and disable security restrictions cause VS Code is weird
            enableScripts: true,
            retainContextWhenHidden: true,
        }
    );
}

export function deactivate() { }

function getHTMLperFile(lineHistorys: interfaces.ExeHistory): interfaces.FileToHTML {
    return utils.objMap(lineHistorys, (value : interfaces.LineMapping) => {
        return getHTMLperLine(value);
    });
}

function getHTMLperLine(lineHistory: interfaces.LineMapping): string[] {
    const newObj = utils.objMap(lineHistory, ( value : interfaces.LineHistory|interfaces.ArgsHistory, key: string) => {
        if ("functionName" in value) {
            return `<div class="line" id="line-${key}">${getHTMLperArgsHistory(value)}</div>`;
        } else {
            return `<div class="line" id="line-${key}">${getHTMLperLineHistory(value)}</div>`;
        }
    });

    // 0 padding
    const maxLine = Math.max(...Object.keys(newObj).map(Number));
    for (let i = 0; i < maxLine; i++) {
        if (!newObj[i]) {
            newObj[i] = `<div class="line" id="line-${i}" ></div>`;
        }
    }

    return Object.values(newObj);


}

function getHTMLperArgsHistory(argsHistory: interfaces.ArgsHistory): string {
    // TODO: implement
    return `<div class="entry column-width" id="name-${argsHistory.functionName}"> </div>`;
}

function getHTMLperLineHistory(lineHistory: interfaces.LineHistory): string {
    const lineHistoryValues = lineHistory.values;
    const lineHistoryValuesHTML = lineHistoryValues.map((value : interfaces.LineHistoryValues) => {
        return `<div class="entry column-width" id="step-${value.step}">${value.value}</div>`;
    });
    return lineHistoryValuesHTML.join("");
}


// TODO: accept other settings other than the default lineHeight of 0 [below 8 is a scalar] [more than 8 is a px value]
// https://github.com/microsoft/vscode/blob/f9480e290f2066edd2e5abab62780ae21b792c1d/src/vs/workbench/contrib/notebook/browser/notebookOptions.ts#L302
function getLineHeight(): number {
    return 19;
    // TODO: fix
    // const defaultLineHeight = 22;
    // const activeTextEditor: vscode.TextEditor = vscode.window.visibleTextEditors[0];
    // if (!activeTextEditor) {
    //     return defaultLineHeight;
    // }

    // // Get the font size from the active text editor's configuration
    // const fontSize = vscode.workspace.getConfiguration('editor').get<number>('fontSize');
    // if (fontSize) {
    //     const lineHeight = Math.round(fontSize * 1.5);
    //     return lineHeight;
    // }

    // // Default line height if font size is not available
    // return defaultLineHeight;
}

function getActiveDocument(): string {
    const activeTextEditor: vscode.TextEditor = vscode.window.visibleTextEditors[0];
    if (!activeTextEditor) {
        return "";
    }
    return activeTextEditor.document.fileName;
}


function getLineHistorys(path: string): interfaces.ExeHistory {
    const data = fs.readFileSync(path, { encoding: 'utf8', flag: 'r' });
    const obj : interfaces.ExeHistory = JSON.parse(data);
    return obj;
}




function getCSS(lineHeight: number): string {
    return `
        <style>
            .lineWrapper {
                position: absolute;
                width: 100%;
            }
            .line {
                display: block;
                max-height: ${lineHeight}px;
                height: ${lineHeight}px;
                position: relative;
                overflow: hidden;
                width: 100%;
            }
            .entry {
                display: block;
                float: left;
                overflow: hidden;
                max-height: ${lineHeight}px;
                height: ${lineHeight}px;
                text-align: center;
                border: 1px solid red;
            }

            .column-width {
                width: 20px;
                max-width: 20px;
            }


            .highlight {
                background-color: var(--vscode-editor-lineHighlightBackground) ;
            }

            .column-highlight {
                background-color: var(--vscode-editor-lineHighlightBackground) ;
                height: 200vh;
                position: fixed;
                top: 0;
                overflow: visible;
                z-index: -1;
            }


        </style>
    `;
}



function getScript(): string {


    return `
        <script>
            function highlightLine(entry) {
                document.querySelectorAll(".highlight").forEach((e) => {
                    e.classList.remove("highlight");
                });

                document.querySelectorAll(".column-highlight").forEach((e) => {
                    e.remove();
                });

                entry.classList.add("highlight");
                entry.parentElement.classList.add("highlight");
                column_highlight = document.createElement("div");
                column_highlight.classList.add("highlight");
                column_highlight.classList.add("column-width");
                column_highlight.classList.add("column-highlight");
                column_highlight.style.left = entry.offsetLeft + entry.offsetWidth + "px";

                entry.appendChild(column_highlight);
            }


            document.querySelectorAll(".entry").forEach((e) => {
                e.addEventListener("click", highlightLine.bind(null, e));
            });

        </script>
    `;
}

