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

  # Corpo do TCC = da página do título/Resumo (a que leva o número 1) até a
  # ÚLTIMA página das Referências. O limite institucional é 25-30 páginas e
  # NÃO conta apêndices nem anexos; as Referências CONTAM.
  #
  # CORRIGIDO EM 2026-10-23 (achado do usuário): a versão anterior media da
  # Introdução até a página em que o título REFERÊNCIAS COMEÇA, apesar de o
  # comentário dizer "até o fim". Reportava 30 quando o real era 37 (pág.
  # física 3 a 39). Os 10 aprovados confirmam a régua nova: o artigo começa
  # na física 3 com o número 1, e as Referências terminam no máximo na
  # física 32, ou seja, na página numerada 30.
  $pgInicio = $null; $pgFim = $null
  foreach ($p in $doc.Paragraphs) {
    $t = $p.Range.Text.Trim()
    if ($pgInicio -eq $null -and $t -match '^Resumo:') {
      $pgInicio = $p.Range.Information(3)
      continue
    }
    if ($p.Style.NameLocal -notlike 'T*tulo 1*') { continue }
    if ($t -match '^(AP.NDICE|ANEXO)') {
      # a página anterior ao 1º Apêndice é a última das Referências
      $pgFim = $p.Range.Information(3) - 1
      $numImpresso = $doc.Range($p.Range.Start, $p.Range.Start).Information(1) - 1
      break
    }
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
    Write-Output "  CORPO:    paginas fisicas $pgInicio ate $pgFim = $corpo paginas, Resumo ate o fim das Referencias ($situacao)"
    Write-Output "            ultima pagina das Referencias leva o numero impresso $numImpresso"
  } else {
    Write-Output "  CORPO:    nao Localizado (verificar os titulos de 1o nivel)"
  }
  $doc.Close($false)
}
finally {
  if ($word) { $word.Quit() }
}