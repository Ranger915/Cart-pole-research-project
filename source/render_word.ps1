$ErrorActionPreference='Stop'
$out=Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent) 'outputs\ieee_revision'
if ((Split-Path $PSScriptRoot -Leaf) -eq 'source') {$out=Split-Path $PSScriptRoot -Parent}
$word=New-Object -ComObject Word.Application
$word.Visible=$false
$word.DisplayAlerts=0
$word.AutomationSecurity=3
$audit=@()
try {
 foreach ($stem in @('revised_ieee_manuscript','revised_detailed_derivations','methodological_response')) {
  $path=Join-Path $out "$stem.docx"
  $pdf=Join-Path $out "$stem.pdf"
  $doc=$word.Documents.Open($path,$false,$false)
  try {
   $doc.Fields.Update() | Out-Null
   $doc.Repaginate()
   $pages=$doc.ComputeStatistics(2)
   $doc.Save()
   $doc.ExportAsFixedFormat($pdf,17)
   $audit+=@{document=$stem;pages=$pages;renderer='Microsoft Word 16';pdf=$pdf}
   Write-Output "$stem rendered pages $pages"
  } finally {$doc.Close(0)}
 }
} finally {$word.Quit()}
$audit | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $out 'results\word_render_audit.json')
