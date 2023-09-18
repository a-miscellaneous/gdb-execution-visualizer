import * as vscode from "vscode";
import * as utils from "./utils";
import * as path from "path";
import * as htmlBuilder from "./html_builder";

export function activate(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand("extension.showHistory", () => {

        const panel = createWebViewPanel();

        const currentFile = path.parse(utils.getActiveDocument()).base;

        const historyPath = utils.getHistoryJsonPath();
        const htmlContent = htmlBuilder.getPureHTML(historyPath);

        const scriptOnDiskPath = vscode.Uri.joinPath(context.extensionUri, 'src', 'webview', 'webview_script.js');
        const scriptPath = panel.webview.asWebviewUri(scriptOnDiskPath).toString();

        const cssOnDiskPath = vscode.Uri.joinPath(context.extensionUri, 'src', 'webview', 'webview_style.css');
        const cssPath = panel.webview.asWebviewUri(cssOnDiskPath).toString();

        setHTMLcontent(panel, htmlContent[currentFile].join(""), scriptPath, cssPath);


        // TODO: test
        vscode.window.onDidChangeTextEditorSelection(() => {
            const currentFile = path.parse(utils.getActiveDocument()).base;
            if (!currentFile) { return; }
            setHTMLcontent(panel, htmlContent[currentFile].join(""), scriptPath, cssPath);
        });


        panel.webview.onDidReceiveMessage(webviewMessageHandler);
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

function createWebViewPanel() {
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



function webviewMessageHandler(message: any) {
    switch (message.command) {
        case "highlight-line":
            utils.changeHighlightedLine(message.id);
            break;
        default:
            console.log("Unknown command: " + message.command);
            break;
    }
}
