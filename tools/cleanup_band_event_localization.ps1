$ErrorActionPreference = 'Stop'

$path = 'localization/simp_chinese/replace/tot_gui_l_simp_chinese.yml'
$lines = Get-Content -LiteralPath $path
$out = New-Object System.Collections.Generic.List[string]

foreach ($line in $lines) {
	if ($line -match '^(\s+kizuna\.(?:20[2-4]|21[1-3]|21[5-9]|22[0-2])\.[a-d]): "(.+?)\\n#P (.+)"\s*$') {
		$key = $Matches[1]
		$name = $Matches[2]
		$effect = '#P ' + $Matches[3]
		$out.Add("${key}: `"$name`"")
		$out.Add("${key}.tt: `"$effect`"")
	} elseif ($line -match '^(\s+kizuna\.20[2-4]\.desc: ".+?)\\n\\n#bold .+?"\s*$') {
		$out.Add($Matches[1] + '"')
	} else {
		$out.Add($line)
	}
}

Set-Content -LiteralPath $path -Value ($out -join "`r`n") -Encoding UTF8
