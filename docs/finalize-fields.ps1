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

  # A medida do CORPO (25-30 páginas) saiu daqui em 2026-11-08 e foi para
  # confere_paginas.ps1, chamado no fim: este script só imprimia o número e
  # saía com 0 mesmo fora da faixa. A régua (Resumo até a última página das
  # Referências, corrigida em 2026-10-23) está documentada lá.

  $doc.Save()
  Write-Output "campos atualizados: $Caminho"
  Write-Output "  paginas:  $paginas"
  Write-Output "  palavras: $palavras"
  Write-Output "  tabelas:  $tabelas"
  Write-Output "  imagens:  $imagens"
  Write-Output "  TOCs:     $($doc.TablesOfContents.Count) sumario + $($doc.TablesOfFigures.Count) lista(s)"
  $doc.Close($false)
}
finally {
  if ($word) { $word.Quit() }
}

# Sai com o código do conferente: corpo fora de 25-30 reprova o passo.
Write-Output ''
& (Join-Path $PSScriptRoot 'confere_paginas.ps1') -Caminho $Caminho
exit $LASTEXITCODE