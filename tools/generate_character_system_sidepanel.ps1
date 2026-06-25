$ErrorActionPreference = 'Stop'

function Convert-GuiRoot {
	param(
		[string]$Source,
		[string]$Output,
		[string]$OldName,
		[string]$NewTypeName,
		[switch]$ConvertGrowthTabs
	)

	$text = Get-Content -LiteralPath $Source -Raw
	$quote = [char]34
	$pattern = 'flowcontainer\s*=\s*\{\s*name\s*=\s*' + $quote + [regex]::Escape($OldName) + $quote
	$match = [regex]::Match($text, $pattern)
	if (-not $match.Success) {
		throw "Could not find GUI root $OldName in $Source"
	}
	$text = $text.Substring($match.Index)
	$replacement = @"
types ${NewTypeName}_types
{
	type $NewTypeName = flowcontainer {
		name = "$NewTypeName"
"@
	$text = [regex]::Replace($text, $pattern, $replacement, 1)
	$text = $text.Replace('JournalEntry.GetCountry.MakeScope', 'GetPlayer.MakeScope')
	$text = $text.Replace('JournalEntry.GetCountry', 'GetPlayer')
	if ($ConvertGrowthTabs) {
		$text = $text.Replace("InformationPanel.SelectTab('tot_character_growth_governor')", "GetVariableSystem.Set('tot_character_growth_page', 'governor')")
		$text = $text.Replace("InformationPanel.SelectTab('tot_character_growth_progress')", "GetVariableSystem.Set('tot_character_growth_page', 'progress')")
		$text = $text.Replace("InformationPanel.IsTabSelected('tot_character_growth_governor')", "GetVariableSystem.HasValue('tot_character_growth_page', 'governor')")
		$text = $text.Replace("InformationPanel.IsTabSelected('tot_character_growth_progress')", "GetVariableSystem.HasValue('tot_character_growth_page', 'progress')")
	}
	$text = $text.Replace('size = { 500 ', 'size = { 1100 ')
	$text = $text.Replace('size = { 520 ', 'size = { 1140 ')
	$text = $text.Replace('size = { 540 ', 'size = { 1180 ')
	$text = $text.Replace('addcolumn = 500', 'addcolumn = 540')
	$text = $text.Replace('addcolumn = 520', 'addcolumn = 560')
	$text = $text.Replace('size = { 49 44 }', 'size = { 107 44 }')
	$text = $text.Replace('size = { 49 34 }', 'size = { 107 34 }')
	$text = $text.Replace('size = { 70 44 }', 'size = { 153 44 }')
	$text = $text.Replace('size = { 70 34 }', 'size = { 153 34 }')
	$text = $text.Replace('size = { 77 44 }', 'size = { 168 44 }')
	$text = $text.Replace('size = { 77 34 }', 'size = { 168 34 }')
	$text = $text.Replace('size = { 111 44 }', 'size = { 244 44 }')
	$text = $text.Replace('size = { 111 34 }', 'size = { 244 34 }')
	$text = $text.Replace('size = { 185 44 }', 'size = { 428 44 }')
	$text = $text.Replace('size = { 185 34 }', 'size = { 428 34 }')
	$text = $text + "`r`n}`r`n"
	Set-Content -LiteralPath $Output -Value $text -Encoding UTF8
}

Convert-GuiRoot `
	-Source 'gui\kizuna_character_list.gui' `
	-Output 'gui\tot_character_system_kizuna_full.gui' `
	-OldName 'widget_je_kizuna_character_list' `
	-NewTypeName 'tot_character_system_kizuna_full'

Convert-GuiRoot `
	-Source 'gui\tot_band_management.gui' `
	-Output 'gui\tot_character_system_band_full.gui' `
	-OldName 'widget_je_tot_band_management' `
	-NewTypeName 'tot_character_system_band_full'

Convert-GuiRoot `
	-Source 'gui\tot_character_growth.gui' `
	-Output 'gui\tot_character_system_growth_full.gui' `
	-OldName 'widget_je_tot_character_growth' `
	-NewTypeName 'tot_character_system_growth_full' `
	-ConvertGrowthTabs
