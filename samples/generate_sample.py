"""Generate a FICTIONAL Swiss home + liability insurance contract (in French) for testing.

Some clauses are deliberately unfavourable to the policyholder. Run:
    python samples/generate_sample.py
"""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).parent / "contrat_assurance_menage_fictif.pdf"

TITLE = "Assurances Lémanique Sereine SA — Police d'assurance ménage et responsabilité civile privée"
HEADER = (
    "<b>DOCUMENT FICTIF — créé uniquement pour des tests. Toute ressemblance avec un assureur réel est fortuite.</b><br/>"
    "Police n° LS-2026-004217 · Preneur d'assurance : Mme Ana Ferreira, Avenue du Tir-Fédéral 12, 1024 Ecublens VD<br/>"
    "Début : 01.12.2026 · Prime annuelle : CHF 289.– · Somme d'assurance ménage : CHF 15'000.–"
)

ARTICLES = [
    ("Art. 1 — Objet de l'assurance",
     "La présente police couvre l'inventaire du ménage du preneur d'assurance au lieu de risque indiqué "
     "contre les dommages causés par l'incendie, les éléments naturels, le dégât d'eau et le vol, ainsi que "
     "la responsabilité civile privée du preneur, dans les limites des présentes Conditions générales (CGA)."),
    ("Art. 2 — Durée et reconduction",
     "Le contrat est conclu pour une durée de cinq (5) ans. À l'échéance, il se renouvelle tacitement pour une "
     "nouvelle période de cinq (5) ans, sauf résiliation notifiée par lettre recommandée parvenue à la Compagnie "
     "au plus tard six (6) mois avant l'échéance. Toute résiliation transmise par courriel ou par un autre moyen "
     "est sans effet."),
    ("Art. 3 — Franchise",
     "Une franchise de CHF 1'000.– est déduite de chaque sinistre, par événement et par catégorie de dommage. "
     "Pour les dommages dus au vol, la franchise est portée à CHF 1'500.–."),
    ("Art. 4 — Indemnisation",
     "Les objets sont indemnisés à leur valeur actuelle au jour du sinistre. Les appareils électroniques "
     "(ordinateurs, téléphones, tablettes, consoles) subissent une dépréciation forfaitaire de 30 % par année "
     "depuis leur date d'achat, la date d'achat devant être prouvée par une facture originale."),
    ("Art. 5 — Sous-assurance",
     "Si la somme d'assurance est inférieure à la valeur de remplacement de l'inventaire du ménage, "
     "l'indemnité est réduite dans la proportion existant entre la somme d'assurance et cette valeur "
     "(règle proportionnelle), y compris pour les sinistres partiels."),
    ("Art. 6 — Vol",
     "Seul le vol avec effraction commis à l'intérieur du logement est couvert. Le vol simple hors du domicile "
     "(sac, téléphone, ordinateur portable en déplacement) ainsi que le vol de vélos, trottinettes et autres "
     "engins de mobilité sont exclus. La couverture n'est accordée que si toutes les portes d'accès étaient "
     "verrouillées à double tour au moment du vol ; à défaut, aucune prestation n'est due."),
    ("Art. 7 — Déclaration de sinistre",
     "Tout sinistre doit être déclaré à la Compagnie par écrit dans un délai de quarante-huit (48) heures dès "
     "sa survenance. Passé ce délai, le preneur est déchu de tout droit à prestation, quelle que soit la cause "
     "du retard."),
    ("Art. 8 — Responsabilité civile privée",
     "La Compagnie couvre la responsabilité civile légale du preneur pour les dommages corporels et matériels "
     "causés à des tiers, jusqu'à CHF 5'000'000.– par événement. Sont exclus les dommages causés aux locaux "
     "loués ou pris à bail par le preneur, y compris les dégâts aux murs, sols, sanitaires et installations "
     "de cuisine, ainsi que tout dommage survenu alors que le preneur se trouvait sous l'influence de l'alcool."),
    ("Art. 9 — Adaptation des primes et des conditions",
     "La Compagnie peut adapter les primes, les franchises et les présentes conditions en tout temps. "
     "La modification est communiquée au preneur au moins dix (10) jours avant son entrée en vigueur et "
     "est réputée acceptée. Elle ne confère au preneur aucun droit de résiliation extraordinaire."),
    ("Art. 10 — Paiement de la prime",
     "La prime est payable annuellement d'avance. En cas de paiement par tranches mensuelles, un supplément "
     "de 12 % est perçu. Les frais de rappel s'élèvent à CHF 50.– par rappel."),
    ("Art. 11 — Protection des données",
     "Le preneur autorise la Compagnie à communiquer ses données personnelles et ses données de sinistre à des "
     "sociétés partenaires à des fins de marketing, sans possibilité de retrait de ce consentement pendant la "
     "durée du contrat."),
    ("Art. 12 — For et droit applicable",
     "Le présent contrat est régi par le droit suisse, notamment la Loi fédérale sur le contrat d'assurance (LCA). "
     "Le for est à Lausanne ou au domicile suisse du preneur d'assurance."),
]


def main() -> None:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm, title="Contrat fictif — test")
    story = [Paragraph(TITLE, styles["Title"]), Paragraph(HEADER, styles["Normal"]), Spacer(1, 0.6 * cm),
             Paragraph("Conditions générales d'assurance (CGA), édition 2026", styles["Heading2"])]
    for heading, body in ARTICLES:
        story += [Paragraph(heading, styles["Heading4"]), Paragraph(body, styles["BodyText"])]
    story += [Spacer(1, 1 * cm), Paragraph("Lu et approuvé — Lieu, date et signature du preneur : ____________________",
                                           styles["Normal"])]
    doc.build(story)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
