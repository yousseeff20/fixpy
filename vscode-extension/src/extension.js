const vscode = require("vscode");
const { execFile } = require("child_process");

const TRACEBACK_HEADER = /Traceback \(most recent call last\):/;
const EXCEPTION_PATTERN = /^([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?:Error|Exception|Warning|Exit|Iteration)): (.+)$/m;

function activate(context) {
  const diagnostics = vscode.languages.createDiagnosticCollection("fixpy");
  context.subscriptions.push(diagnostics);

  const analyzeSelectionCmd = vscode.commands.registerCommand(
    "fixpy.analyzeSelection",
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage("No active editor found.");
        return;
      }

      const selectionText = editor.document.getText(editor.selection);
      const fullText = editor.document.getText();
      const text = selectionText.trim() ? selectionText : fullText;

      if (!looksLikeTraceback(text)) {
        vscode.window.showInformationMessage(
          "No traceback detected in selection/document."
        );
        return;
      }

      const result = await runFixpy(text);
      if (!result.ok) {
        vscode.window.showErrorMessage(result.message);
        return;
      }

      showAnalysis(result.data);
      if (result.data.fix) {
        await context.workspaceState.update("fixpy.lastFix", result.data.fix);
      }
    }
  );

  const analyzeDocumentCmd = vscode.commands.registerCommand(
    "fixpy.analyzeDocument",
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage("No active editor found.");
        return;
      }
      const text = editor.document.getText();
      const result = await runFixpy(text);
      if (!result.ok) {
        vscode.window.showErrorMessage(result.message);
        return;
      }
      showAnalysis(result.data);
      if (result.data.fix) {
        await context.workspaceState.update("fixpy.lastFix", result.data.fix);
      }
    }
  );

  const copyTopFixCmd = vscode.commands.registerCommand(
    "fixpy.copyTopFix",
    async () => {
      const fix = context.workspaceState.get("fixpy.lastFix");
      if (!fix) {
        vscode.window.showInformationMessage(
          "No fix suggestion available yet. Run a fixpy analysis first."
        );
        return;
      }
      await vscode.env.clipboard.writeText(String(fix));
      vscode.window.showInformationMessage("Copied top fix suggestion to clipboard.");
    }
  );

  context.subscriptions.push(analyzeSelectionCmd, analyzeDocumentCmd, copyTopFixCmd);

  const refreshDiagnostics = (doc) => {
    if (
      !vscode.workspace.getConfiguration("fixpy").get("autoDetectTracebacks", true)
    ) {
      diagnostics.delete(doc.uri);
      return;
    }

    const text = doc.getText();
    if (!looksLikeTraceback(text)) {
      diagnostics.delete(doc.uri);
      return;
    }

    diagnostics.set(doc.uri, extractTracebackDiagnostics(text));
  };

  if (vscode.window.activeTextEditor) {
    refreshDiagnostics(vscode.window.activeTextEditor.document);
  }

  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(refreshDiagnostics),
    vscode.workspace.onDidChangeTextDocument((evt) => refreshDiagnostics(evt.document)),
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (editor) refreshDiagnostics(editor.document);
    })
  );

  context.subscriptions.push(
    vscode.languages.registerCodeActionsProvider(
      [{ scheme: "file" }, { scheme: "untitled" }],
      new FixpyCodeActionProvider(),
      {
        providedCodeActionKinds: [vscode.CodeActionKind.QuickFix]
      }
    )
  );
}

function deactivate() {}

function looksLikeTraceback(text) {
  return TRACEBACK_HEADER.test(text) && EXCEPTION_PATTERN.test(text);
}

function extractTracebackDiagnostics(text) {
  const lines = text.split(/\r?\n/);
  const exceptionMatch = EXCEPTION_PATTERN.exec(text);
  const exceptionText = exceptionMatch
    ? `${exceptionMatch[1]}: ${exceptionMatch[2]}`
    : "Python traceback detected";

  const results = [];
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const frameMatch = line.match(/^\s+File ".+", line \d+(?:, in .+)?$/);
    if (!frameMatch) continue;

    const range = new vscode.Range(i, 0, i, line.length);
    const diag = new vscode.Diagnostic(
      range,
      `${exceptionText} (frame)`,
      vscode.DiagnosticSeverity.Error
    );
    diag.source = "fixpy";
    results.push(diag);
  }

  return results;
}

function runFixpy(inputText) {
  return new Promise((resolve) => {
    const config = vscode.workspace.getConfiguration("fixpy");
    const command = config.get("command", "fixpy");
    const lang = config.get("language", "en");
    const maxBufferMB = Number(config.get("maxBufferMB", 5));
    const maxBuffer = Math.max(1, maxBufferMB) * 1024 * 1024;

    const child = execFile(command, ["--json", "--lang", lang], { maxBuffer }, (error, stdout, stderr) => {
      if (error) {
        const details = stderr?.trim() || error.message;
        resolve({
          ok: false,
          message: `Failed to run '${command}'. Ensure fixpy is installed and in PATH. ${details}`
        });
        return;
      }

      try {
        const parsed = JSON.parse(stdout);
        resolve({ ok: true, data: parsed });
      } catch {
        resolve({
          ok: false,
          message: `fixpy returned invalid JSON output. Output: ${stdout || stderr}`
        });
      }
    });

    child.stdin.write(inputText);
    child.stdin.end();
  });
}

function showAnalysis(data) {
  const lines = [
    `Exception: ${data.exception_type || "Unknown"}`,
    "",
    "What happened:",
    data.cause || "-",
    "",
    "Explanation:",
    data.explanation || "-",
    "",
    "How to fix:",
    data.fix || "-",
  ];

  if (Array.isArray(data.smart_suggestions) && data.smart_suggestions.length) {
    lines.push("", "Quick suggestions:");
    for (const suggestion of data.smart_suggestions.slice(0, 5)) {
      lines.push(`- ${suggestion}`);
    }
  }

  if (data.location && data.location.file) {
    lines.push(
      "",
      "Detected location:",
      `${data.location.file}:${data.location.line || "?"}`
    );
  }

  const panel = vscode.window.createOutputChannel("fixpy Analysis");
  panel.clear();
  panel.appendLine(lines.join("\n"));
  panel.show(true);
}

class FixpyCodeActionProvider {
  provideCodeActions(document, range, context) {
    const hasFixpyDiagnostic = context.diagnostics.some((d) => d.source === "fixpy");
    if (!hasFixpyDiagnostic) return [];

    const explainAction = new vscode.CodeAction(
      "Explain traceback with fixpy",
      vscode.CodeActionKind.QuickFix
    );
    explainAction.command = {
      command: "fixpy.analyzeSelection",
      title: "Analyze traceback"
    };

    return [explainAction];
  }
}

module.exports = {
  activate,
  deactivate,
};
