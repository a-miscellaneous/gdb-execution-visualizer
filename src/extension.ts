import * as vscode from "vscode";
import * as fs from "fs";
import * as interfaces from "./interfaces";
import * as utils from "./utils";
import * as path from "path";
import * as htmlBuilder from "./html_builder";

export function activate(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand("extension.showHistory", () => {

        const panel = createWebViewPanel(context);
        const currentFile = path.parse(utils.getActiveDocument()).base;

        const historyPath = utils.getHistoryJsonPath();
        const htmlContent = htmlBuilder.getPureHTML(historyPath)[currentFile].join(""); // TODO: adapt to multiple files

        const scriptOnDiskPath = vscode.Uri.joinPath(context.extensionUri, 'src', 'webview', 'webview_script.js');
        const scriptPath = panel.webview.asWebviewUri(scriptOnDiskPath).toString();

        const cssOnDiskPath = vscode.Uri.joinPath(context.extensionUri, 'src', 'webview', 'webview_style.css');
        const cssPath = panel.webview.asWebviewUri(cssOnDiskPath).toString();

        setHTMLcontent(panel, htmlContent, scriptPath, cssPath);
    });

    context.subscriptions.push(disposable);
}

function setHTMLcontent(panel: vscode.WebviewPanel, htmlContent: string, scriptPath: string, cssPath: string) {
    const css = getCSS(utils.getLineHeight());
    panel.webview.html = `
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <link href="${cssPath}" rel="stylesheet">
                    <title>History</title>
                    ${css}
                </head>
                <body>
                    <div class="lineWrapper">
                    ${htmlContent}
                    </div>
                    <script src="${scriptPath}"></script>
                </body>
            </html>
        `;
}

function createWebViewPanel(context: vscode.ExtensionContext) {
    return vscode.window.createWebviewPanel(
        "historyWebView", // id
        "History", //title
        vscode.ViewColumn.Beside, //spawn location
        { enableScripts: true }
    );
}

export function deactivate() { }



function getCSS(lineHeight: number): string {
    return `
        <style>
            .editor-height {
                height: ${lineHeight}px;
                max-height: ${lineHeight}px;
            }
        </style>
    `;
}


