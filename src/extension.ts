import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";
import { get } from "http";

interface HistoryEntry {
    line: number;
    value?: string;
    args?: Object;
    file: string;
    type: string;
    var?: string;
}


export function activate(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand( "extension.showHistory",  () => {

        const panel = createWebViewPanel();
        const lineHeight = getLineHeight();
        console.log("Line Height:", lineHeight);
        const filePath = vscode.Uri.file(path.join(context.extensionPath, "history.json"));
        const lineHistorys = getLineHistorys(filePath.fsPath);
        const historyPerLine: string[][] = getHistoryPerLine(lineHistorys);
        const htmlPerLine: string[] = getHTMLPerLine(historyPerLine);
        const htmlContent = htmlPerLine.map((html) => `<div class="line" >${html}</div>`).join("");

        // Set the webview's HTML content
        setHTMLcontent(panel, htmlContent, lineHeight);

    });

    context.subscriptions.push(disposable);
}

function setHTMLcontent(panel: vscode.WebviewPanel, htmlContent: string, lineHeight: number) {
    const css = getCSS(lineHeight);
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
                </body>
            </html>
        `;
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


function getLineHistorys(path: string): HistoryEntry[] {
    const data = fs.readFileSync(path, { encoding: 'utf8', flag: 'r' });
    const lines = data.split("\n");
    const historyEntries: HistoryEntry[] = [];
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (line === "") { // Skip empty lines
            continue;
        }
        const entry: HistoryEntry = JSON.parse(line);
        historyEntries.push(entry);
    }
    return historyEntries;
}


function getHistoryPerLine(lineHistorys: HistoryEntry[]): string[][] {
    const historyPerLine: string[][] = [];
    for (let i = 0; i < lineHistorys.length; i++) {
        const historyEntry = lineHistorys[i];
        const line = historyEntry.line;
        if (historyPerLine[line] === undefined) {
            historyPerLine[line] = [];
        }

        if (historyEntry.type === "assignment") {
            historyPerLine[line].push(historyEntry.value as string);
        } else {
            historyPerLine[line].push(JSON.stringify(historyEntry.args));
        }
    }

    // 0 pad empty lines
    for (let i = 0; i < historyPerLine.length; i++) {
        if (historyPerLine[i] === undefined) {
            historyPerLine[i] = [];
        }
    }
    return historyPerLine;
}

function getCSS(lineHeight: number): string {
    return `
        <style>
            .lineWrapper {
                position: absolute;
            }
            .line {
                display: block;
                max-height: ${lineHeight}px;
                height: ${lineHeight}px;
                position: relative;
                overflow: hidden;
            }
            .entry {
                display: block;
                float: left;
                overflow: hidden;
                max-height: ${lineHeight}px;
                height: ${lineHeight}px;
                margin-right: 10px;
        </style>
    `;
}

function getHTMLPerLine(historyPerLine: string[][]): string[] {
    const htmlPerLine: string[] = [];
    for (let i = 0; i < historyPerLine.length; i++) {
        const line = historyPerLine[i];
        const html = line.map((entry) => `<div class="entry">${entry}</div>`).join("");
        htmlPerLine.push(html);
    }
    return htmlPerLine;
}