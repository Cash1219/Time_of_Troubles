$ErrorActionPreference = 'Stop'

$path = 'gui\information_panel_bar.gui'
$text = Get-Content -LiteralPath $path -Raw

$clearLine = "`t`t`t`t`t`tonclick = ""[GetVariableSystem.Clear('tot_character_system_panel_open')]"""
$targets = @(
	'onclick = "[InformationPanelBar.OpenPanel(',
	'onclick = "[InformationPanelBar.OpenPanelCycleTabs',
	'onclick = "[InformationPanelBar.OpenCompactBuildingBrowserPanel',
	'onclick = "[InformationPanelBar.OpenMarketPanel',
	'onclick = "[MapListPanelManager.ToggleCurrentPanel]'
)

foreach ($target in $targets) {
	$text = $text.Replace($target, $clearLine + "`r`n`t`t`t`t`t`t" + $target)
}

$lines = $text -split "`r?`n"
$deduped = New-Object System.Collections.Generic.List[string]
$lastWasClear = $false
foreach ($line in $lines) {
	$isClear = $line -like "*GetVariableSystem.Clear('tot_character_system_panel_open')*"
	if ($isClear -and $lastWasClear) {
		continue
	}
	$deduped.Add($line)
	$lastWasClear = $isClear
}
$text = ($deduped -join "`r`n")

Set-Content -LiteralPath $path -Value $text -Encoding UTF8
