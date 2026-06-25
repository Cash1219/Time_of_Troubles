$ErrorActionPreference = 'Stop'

$path = 'localization/simp_chinese/replace/tot_gui_l_simp_chinese.yml'
$text = Get-Content -LiteralPath $path -Raw

$text = $text.Replace("[Country.GetCustom('tot_band_pending_event_band_loc')]", "[SCOPE.GetRootScope.GetCountry.GetCustom('tot_band_pending_event_band_loc')]")
foreach ($i in 1..10) {
	$text = $text.Replace("[Country.GetCustom('tot_band_${i}_name_loc')]", "[SCOPE.GetRootScope.GetCountry.GetCustom('tot_band_${i}_name_loc')]")
}

Set-Content -LiteralPath $path -Value $text -Encoding UTF8
