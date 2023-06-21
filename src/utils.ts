import * as vscode from 'vscode';
import * as path from 'path';

export function objMap(obj: object, fn: Function) {
    return Object.fromEntries(Object.entries(obj).map(([key, value]) => [key, fn(value, key)]));
}

export function getLineHeight(): number {
    // from internal https://github.com/microsoft/vscode/blob/8d87a664274d23477388e750d40d4ab942c83751/src/vs/editor/common/config/fontInfo.ts#L54-L58
    const GOLDEN_LINE_HEIGHT_RATIO = 1.35; // add mac support
    const MINIMUM_LINE_HEIGHT = 8;
    var lineHeight = vscode.workspace.getConfiguration("editor").get<number>("lineHeight")!!;
    const fontSize = vscode.workspace.getConfiguration("editor").get<number>("fontSize")!!;

    if (lineHeight === 0) { // 0 is the default
        lineHeight = Math.round(GOLDEN_LINE_HEIGHT_RATIO * fontSize); // fontSize is editor.fontSize
    } else if (lineHeight < MINIMUM_LINE_HEIGHT) {
        lineHeight = MINIMUM_LINE_HEIGHT;
    }
    return lineHeight;
}


export function getHistoryJsonPath(): string {
    const root = vscode.workspace.workspaceFolders;
    if (!root) { return ""; }
    const historyPath = path.join(root[0].uri.fsPath, ".vscode", "history.json");
    return historyPath;
}

export function getActiveDocument(): string {
    const activeTextEditor: vscode.TextEditor = vscode.window.visibleTextEditors[0];
    if (!activeTextEditor) {
        return "";
    }
    return activeTextEditor.document.fileName;
}

export function changeHighlightedLine(id: string) {
    const textEditor: vscode.TextEditor = vscode.window.visibleTextEditors[0];
}