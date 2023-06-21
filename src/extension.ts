import * as vscode from "vscode";
import * as fs from "fs";
import * as interfaces from "./interfaces";
import * as utils from "./utils";
import * as path from "path";
import * as htmlBuilder from "./html_builder";






export function activate(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand("extension.showHistory", () => {

        const panel = createWebViewPanel(context);
        const currentFile = path.parse(getActiveDocument()).base;
        const root = vscode.workspace.workspaceFolders;
        if (!root) { return; }


        const historyPath = path.join(root[0].uri.fsPath, ".vscode", "history.json");




        const htmlContent = htmlBuilder.getPureHTML(historyPath)[currentFile].join("");
        const onDiskPath = vscode.Uri.joinPath(context.extensionUri, 'src', 'webview_script.js');
        const scriptPath = panel.webview.asWebviewUri(onDiskPath);

        // Set the webview's HTML content
        const lineHeight = getLineHeight();
        setHTMLcontent(panel, htmlContent, lineHeight, scriptPath);

    });

    context.subscriptions.push(disposable);
}

function setHTMLcontent(panel: vscode.WebviewPanel, htmlContent: string, lineHeight: number, scriptPath: vscode.Uri) {
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
                    <script src="${scriptPath.toString()}"></script>
                </body>
            </html>
        `;
    console.log("HTML Content:", panel.webview.html);
}

function createWebViewPanel(context: vscode.ExtensionContext) {
    return vscode.window.createWebviewPanel(
        "historyWebView", // id
        "History", //title
        vscode.ViewColumn.Beside, //spawn location
        {   // Enable JavaScript and disable security restrictions cause VS Code is weird
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: [vscode.Uri.joinPath(context.extensionUri, 'src')]
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

function getActiveDocument(): string {
    const activeTextEditor: vscode.TextEditor = vscode.window.visibleTextEditors[0];
    if (!activeTextEditor) {
        return "";
    }
    return activeTextEditor.document.fileName;
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
                position: absolute;
                overflow: hidden;
                max-height: ${lineHeight}px;
                height: ${lineHeight}px;
                text-align: center;
                background-color: #46463f;
            }

            .column-width {
                width: 20px;
                max-width: 20px;
            }


            .highlight {
                background-color: var(--vscode-editor-lineHighlightBackground) ;
            }

            .column-highlight {
                position: absolute;
                z-index: -1;
                overflow: visible;


            }


        </style>
    `;
}


