$src = "c:\Users\thoma\Desktop\lostinfinity-1.16.41 - Copy\assets\lostinfinity\textures\items"
$dst = "C:\Users\thoma\Desktop\AbyssalWeapons\src\main\resources\assets\abyssalweapons\textures\item"

$copies = @(
    "astrallium_condensed.png:astrallium_alloy.png",
    "crystonium_condensed.png:crystonium_alloy.png",
    "hextorium_condensed.png:hextorium_alloy.png",
    "vellorium_condensed.png:vellorium_alloy.png",
    "incadium_condensed.png:incadium_alloy.png",
    "laser_blade.png:laser_blade.png",
    "dueling_sword_dull.png:dueling_sword_dull.png",
    "dueling_sword_sharp.png:dueling_sword_sharp.png",
    "dueling_sword_razor_edged.png:dueling_sword_razor_edged.png",
    "phantom_blade.png:phantom_blade.png",
    "hexbreaker.png:hexbreaker.png",
    "rapier_of_revenge.png:rapier_of_revenge.png",
    "blade_of_the_conqueror.png:blade_of_the_conqueror.png",
    "saber_claw.png:saber_claw.png",
    "blade_of_the_forbidden.png:blade_of_the_forbidden.png",
    "bladesofconvergence.png:blades_of_convergence.png",
    "world_splitter.png:world_splitter.png",
    "the_apex.png:the_apex.png",
    "razor_of_infinity.png:razor_of_infinity.png",
    "realm_cracker.png:realm_cracker.png",
    "lost_blades_of_infinity.png:lost_blades_of_infinity.png",
    "mirror_shield.png:mirror_shield.png",
    "serpentine_shield.png:serpentine_shield.png",
    "elementium_bow_fire.png:elementium_bow_mk1.png",
    "elementium_bow_electric.png:elementium_bow_mk2.png",
    "prime_elementium_bow.png:elementium_bow_mk3.png"
)

foreach ($c in $copies) {
    $parts = $c.Split(':')
    $s = Join-Path $src $parts[0]
    $d = Join-Path $dst $parts[1]
    if (Test-Path $s) {
        Copy-Item $s $d
        Write-Host "OK: $($parts[1])"
    } else {
        Write-Host "MISSING: $($parts[0])"
    }
}
