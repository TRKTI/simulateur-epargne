duree_placement = 6  # années
gain = 2000  # € de plus-value

if duree_placement < 5:
    impot = gain * 0.30  # flat tax 30%
else:
    impot = gain * 0.172  # PEA après 5 ans : que les prélèvements sociaux

print("Impôt à payer :", round(impot, 2), "€")