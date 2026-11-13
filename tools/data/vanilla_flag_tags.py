"""Country tags for which the base game ships its own ideology flags (gfx/flags/TAG_democratic.tga ...).

The engine prefers TAG_<ideology>.tga over TAG.tga, so a mod country that reuses one of these tags would
fly the base game's flag (Rome = ROM flew the flag of Romania). tools/world.py therefore writes the four
ideology flags as well for every tag listed here. Read from the game's gfx/flags (1.19.5); to refresh:
    python tools/data/vanilla_flag_tags.py     (needs the game)
"""

VANILLA_FLAG_TAGS = set("""
    ABK ADU AFA AFG ALB ALG ALT ANG ANU AOI ARG ARM AST ASY ATJ AUS
    AZR BAH BAN BAR BAS BAY BEG BEL BHR BHU BIA BIH BLC BLI BLR BLZ
    BOL BOS BOT BOU BRA BRD BRI BRM BRN BSK BUK BUL BUR BYA CAM CAN
    CAR CAT CAY CBV CHA CHI CHL CHM CHR CHU CIN CIP CKK CMR COG COL
    COR COS CPS CRC CRI CRO CSA CUB CYP CZE DAG DAH DDR DEN DJI DOM
    DON ECU EGY ELS ENG EQG ERI EST ETH EVE EZO FER FIJ FIN FOR FRA
    FSA FSM GAB GAL GAM GAR GBA GDC GDL GEN GEO GER GHA GLC GNA GNB
    GOW GRE GRN GSM GUA GUM GXC GYA HAI HAN HAR HAW HBC HES HET HOL
    HON HRZ HUN HYD IAS ICE IMO INC INS INU IRE IRQ ISR ITA ITZ IVO
    JAM JAN JAP JOR KAL KAR KAS KAT KAZ KBK KEN KGZ KHA KHI KHL KHM
    KKP KLT KOL KOM KOR KOS KSH KUB KUM KUR KUW KYR LAO LAT LBA LBV
    LEB LIB LIT LKA LUX MAC MAD MAE MAL MAN MAR MAY MDA MEK MEL MEN
    MEX MIS MKD MLD MLI MLT MLW MNT MOL MON MOR MPU MRT MYS MZB NAH
    NAV NEN NEP NGA NGR NIC NIR NMB NOA NOR NWF NXM NZL OCC OKN OMA
    ORO OVO PAK PAL PAN PAP PAR PER PHI PLU PNG POK POL POR PRC PRE
    PRU PSH PSR PUE QAT QEM QUE RAA RAJ RAN RAP RAR RAS RCG RCO RGB
    RHD RHI RIF RIG RJP RKA RKC RKI RKK RKL RKM RKN RKO RKT RKU RKV
    RNA RNG ROA ROM RUS RWA SAB SAF SAM SAR SAU SAX SCO SEN SER SHL
    SHX SIA SIC SID SIE SIK SIL SIN SKK SLO SLV SMI SND SNG SOK SOL
    SOM SOV SPA SPM SPR SRL SSI SUD SUR SVN SWE SWI SYR TAH TAJ TAN
    TAT TAY THU TIB TIG TJK TKM TML TMS TNE TOG TOS TRA TRI TRN TTS
    TUN TUR TZN UAE UBD UDM UGA UKR URG USA USB UZB VAN VEN VGE VIN
    VLA VOL WES WGR WIS WLS WPG WUR XIC XSM YAK YAM YEM YUC YUG YUN
    ZAM ZIM
""".split())


if __name__ == "__main__":
    import re
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import mapdata
    found = set()
    for fp in (mapdata.GAME / "gfx" / "flags").glob("*.tga"):
        m = re.match(r"([A-Z0-9]{3})_(democratic|fascism|communism|neutrality)$", fp.stem)
        if m:
            found.add(m.group(1))
    print(len(found), "tags; new:", sorted(found - VANILLA_FLAG_TAGS), "gone:", sorted(VANILLA_FLAG_TAGS - found))
