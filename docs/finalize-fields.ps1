# Atualiza os campos do .docx do TCC e salva.
#
# POR QUE EXISTE: o build_tcc_docx.py insere campos do Word (TOC do
# SUMARIO, TOC \c da Lista de Quadros/Ilustracoes e SEQ da numeracao). Esses
# campos nascem vazios - o Word so preenche quando "atualiza campos". Sem
# este passo o documento sai com o SUMARIO em branco e os Quadros sem numero.
#
# Uso (PowerShell):
#   .\docs\finalize-fields.ps1
#   .\docs\finalize-fields.ps1 -Caminho 'C:\...\tcc2_final.docx'
param(
  [string]$Caminho = (Join-Path (Split-Path -Parent $PSScriptRoot) 'docs\tcc2_final.docx')
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Caminho)) {
  throw "arquivo nao encontrado: $Caminho"
}

$word = $null
try {
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0

  $doc = $word.Documents.Open((Resolve-Path $Caminho).Path, $false, $false)

  # Duas passadas: a primeira gera o SUMARIO/Lista, a segunda preenche os
  # numeros de pagina que a propria insercao do sumario desloca.
  foreach ($passo in 1..2) {
    foreach ($story in $doc.StoryRanges) { $story.Fields.Update() | Out-Null }
    $doc.Repaginate()
  }
  # os TOCs precisam de update explicito (nao respondem ao Fields.Update do story)
  foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
  foreach ($tof in $doc.TablesOfFigures) { $tof.Update() }
  $doc.Repaginate()

  $paginas = $doc.ComputeStatistics(2)
  $palavras = $doc.ComputeStatistics(0)
  $tabelas = $doc.Tables.Count
  $imagens = $doc.InlineShapes.Count

  # Corpo do TCC = da Seção 1 até o fim da Referências. O limite
  # institucional é 25-30 páginas e NÃO conta apêndices nem anexos, então o
  # total do documento não serve: até 2026-10-04 o "21" que aparecia no
  # `tcc2_texto.md` era derivação manual (total menos pré-textual menos
  # anexos), sem artefato — o que viola a regra do projeto de número que
  # sempre vem de medição.
  $pgInicio = $null; $pgFim = $null
  foreach ($p in $doc.Paragraphs) {
    if ($p.Style.NameLocal -notlike 'T*tulo 1*') { continue }
    $t = $p.Range.Text.Trim()
    if ($pgInicio -eq $null -and $t -match '^1\s+INTRODU') {
      $pgInicio = $p.Range.Information(3)
    }
    if ($t -match '^REFER') { $pgFim = $p.Range.Information(3); break }
  }
  $corpo = if ($pgInicio -and $pgFim) { $pgFim - $pgInicio + 1 } else { $null }

  $doc.Save()
  Write-Output "campos atualizados: $Caminho"
  Write-Output "  paginas:  $paginas"
  Write-Output "  palavras: $palavras"
  Write-Output "  tabelas:  $tabelas"
  Write-Output "  imagens:  $imagens"
  Write-Output "  TOCs:     $($doc.TablesOfContents.Count) sumario + $($doc.TablesOfFigures.Count) lista(s)"
  if ($corpo) {
    # Faixa institucional 25-30. O corpo esta em 30, o TETO exato: cabe,
    # mas nao ha folga. Qualquer acréscimo de texto empurra para fora, e o
    # script tem de dizer isso em voz alta em vez de so reportar o numero.
    $situacao = if ($corpo -lt 25) { 'ABAIXO do minimo de 25' }
                elseif ($corpo -gt 30) { 'ACIMA do maximo de 30' }
                elseif ($corpo -eq 30) { 'NO TETO da faixa 25-30 - sem folga, qualquer acréscimo empurra para fora' }
                else { 'dentro da faixa 25-30' }
    Write-Output "  CORPO:    paginas $pgInicio ate $pgFim = $corpo paginas ($situacao)"
  } else {
    Write-Output "  CORPO:    nao Localizado (verificar os titulos de 1o nivel)"
  }
  $doc.Close($false)
}
finally {
  if ($word) { $word.Quit() }
}