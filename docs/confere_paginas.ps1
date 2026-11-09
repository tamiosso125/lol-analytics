# Confere as paginas do corpo do TCC e de cada apendice, pelo proprio Word.
#
# POR QUE EXISTE: o corpo esta em 30 paginas, o TETO da faixa institucional
# 25-30, sem folga. O finalize-fields.ps1 media e IMPRIMIA o numero, mas
# saia com 0 mesmo acima do limite: quem nao lesse a saida entregava fora da
# regra. Em 2026-11-08 o Apendice A vazou duas linhas para uma pagina nova
# (commit cda4da5) e so a leitura do documento pegou. Este script sai com 1 quando o
# corpo sai da faixa e lista as paginas de cada apendice.
#
# REGUA (2026-10-23, conferida contra os 10 trabalhos aprovados): corpo = da
# pagina do Resumo (a que leva o numero 1) ate a ULTIMA pagina das
# Referencias, ou seja, a pagina anterior ao 1o Apendice. Apendices e
# anexos nao contam; as Referencias contam.
#
# Abre o .docx SO LEITURA e nao salva. Rode depois do finalize-fields.ps1
# (que chama este script no fim).
#
# Uso (PowerShell):
#   .\docs\confere_paginas.ps1
#   .\docs\confere_paginas.ps1 -Caminho 'C:\...\tcc2_final.docx' -Maximo 30
param(
  [string]$Caminho = (Join-Path (Split-Path -Parent $PSScriptRoot) 'docs\tcc2_final.docx'),
  [int]$Minimo = 25,
  [int]$Maximo = 30
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path $Caminho)) { throw "arquivo nao encontrado: $Caminho" }

$falhas = @()
$word = $null
try {
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0
  # Open(FileName, ConfirmConversions, ReadOnly)
  $doc = $word.Documents.Open((Resolve-Path $Caminho).Path, $false, $true)
  $doc.Repaginate()
  $total = $doc.ComputeStatistics(2)

  $pgInicio = $null
  $apendices = @()
  foreach ($p in $doc.Paragraphs) {
    $t = $p.Range.Text.Trim()
    if ($null -eq $pgInicio) {
      if ($t -match '^Resumo:') { $pgInicio = $p.Range.Information(3) }
      continue
    }
    if ($p.Style.NameLocal -notlike 'T*tulo 1*') { continue }
    if ($t -match '^(AP.NDICE|ANEXO)') {
      $apendices += [pscustomobject]@{ Titulo = $t; Pagina = $p.Range.Information(3) }
    }
  }
  $doc.Close($false)

  if ($null -eq $pgInicio) { $falhas += 'paragrafo "Resumo:" nao encontrado: inicio do corpo desconhecido' }
  if ($apendices.Count -eq 0) { $falhas += 'nenhum titulo de 1o nivel APENDICE/ANEXO: fim do corpo desconhecido' }

  if ($falhas.Count -eq 0) {
    $pgFim = $apendices[0].Pagina - 1
    $corpo = $pgFim - $pgInicio + 1
    $situacao = if ($corpo -lt $Minimo) { "ABAIXO do minimo de $Minimo" }
                elseif ($corpo -gt $Maximo) { "ACIMA do maximo de $Maximo" }
                elseif ($corpo -eq $Maximo) { 'no teto, sem folga: qualquer acrescimo empurra para fora' }
                else { "dentro da faixa, folga de $($Maximo - $corpo)" }
    Write-Output "Documento: $total paginas fisicas"
    Write-Output "CORPO:     paginas fisicas $pgInicio a $pgFim = $corpo ($Minimo-$Maximo; $situacao)"
    if ($corpo -lt $Minimo -or $corpo -gt $Maximo) { $falhas += "corpo com $corpo paginas, fora da faixa $Minimo-$Maximo" }

    Write-Output ''
    Write-Output 'Apendices (paginas cada; apendice que passa de 1 pagina por poucas linhas merece olhar):'
    for ($i = 0; $i -lt $apendices.Count; $i++) {
      $ini = $apendices[$i].Pagina
      $fim = if ($i + 1 -lt $apendices.Count) { $apendices[$i + 1].Pagina - 1 } else { $total }
      $n = [math]::Max(1, $fim - $ini + 1)
      $titulo = $apendices[$i].Titulo
      if ($titulo.Length -gt 70) { $titulo = $titulo.Substring(0, 70) + '...' }
      Write-Output ("  {0,3} pag. (fis. {1}-{2})  {3}" -f $n, $ini, $fim, $titulo)
    }
  }
}
finally {
  if ($word) { $word.Quit() }
}

Write-Output ''
if ($falhas.Count -gt 0) {
  foreach ($f in $falhas) { Write-Output "FALHA: $f" }
  Write-Output 'VEREDITO: fora da regra'
  exit 1
}
Write-Output 'VEREDITO: corpo dentro da faixa'
exit 0
