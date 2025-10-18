import streamlit as st
import pandas as pd
import altair as alt

KWH_PER_L_PETROL = 8.9
KWH_PER_L_DIESEL = 9.7


def compute_totals(
    km_total,
    hyb_l_per_100,
    hyb_kwh_per_100,
    diesel_l_per_100,
    bev_kwh_per_100,
    price_petrol,
    price_diesel,
    price_kwh,
    co2_petrol,
    co2_diesel,
    co2_grid,
):
    factor = km_total / 100.0

    hyb_l_total = hyb_l_per_100 * factor
    hyb_kwh_total = hyb_kwh_per_100 * factor
    hyb_cost = hyb_l_total * price_petrol + hyb_kwh_total * price_kwh
    hyb_co2_kg = hyb_l_total * co2_petrol + hyb_kwh_total * co2_grid
    hyb_energy_kwh_per_100 = hyb_l_per_100 * KWH_PER_L_PETROL + hyb_kwh_per_100
    hyb_energy_total_kwh = hyb_energy_kwh_per_100 * factor

    d_l_total = diesel_l_per_100 * factor
    d_cost = d_l_total * price_diesel
    d_co2_kg = d_l_total * co2_diesel
    d_energy_kwh_per_100 = diesel_l_per_100 * KWH_PER_L_DIESEL
    d_energy_total_kwh = d_energy_kwh_per_100 * factor

    bev_kwh_total = bev_kwh_per_100 * factor
    bev_cost = bev_kwh_total * price_kwh
    bev_co2_kg = bev_kwh_total * co2_grid

    factor_nonzero = factor if factor else 1

    df = pd.DataFrame(
        {
            "Hybrid (BMW 330e)": {
                "Energie (kWh/100km)": hyb_energy_kwh_per_100,
                "Energie gesamt (kWh)": hyb_energy_total_kwh,
                "Kosten/100km (€)": hyb_cost / factor_nonzero,
                "Kosten gesamt (€)": hyb_cost,
                "CO2 (g/km)": (hyb_co2_kg * 1000 / km_total) if km_total else 0,
            },
            "Diesel (BMW 330d)": {
                "Energie (kWh/100km)": d_energy_kwh_per_100,
                "Energie gesamt (kWh)": d_energy_total_kwh,
                "Kosten/100km (€)": d_cost / factor_nonzero,
                "Kosten gesamt (€)": d_cost,
                "CO2 (g/km)": (d_co2_kg * 1000 / km_total) if km_total else 0,
            },
            "BEV (BMW i4 / VW ID.7)": {
                "Energie (kWh/100km)": bev_kwh_per_100,
                "Energie gesamt (kWh)": bev_kwh_total,
                "Kosten/100km (€)": bev_cost / factor_nonzero,
                "Kosten gesamt (€)": bev_cost,
                "CO2 (g/km)": (bev_co2_kg * 1000 / km_total) if km_total else 0,
            },
        }
    ).T

    return df


def main():
    st.set_page_config(page_title="Fahrzeugvergleich", layout="wide")
    st.title("Vergleichs-Tool Hybrid vs. Diesel vs. BEV")
    st.write(
        """
        **Annahmen beruhen auf beispielhaften Modellen:**
        - Hybrid: abgelesene Daten aus BMW 330e mit Benzin+Strom
        - Diesel: z.B. BMW 330d
        - BEV: z.B. VW ID.7 oder BMW i4
        
        **Was kann ich hier einstellen?**
        - Gesamt-km
        - Hybrid: Benzin (l/100 km) + Strom (kWh/100 km)
        - Diesel: l/100 km
        - BEV: kWh/100 km
        - Preise: Benzin €/l, Diesel €/l, Strom €/kWh
        - CO₂-Faktoren: Benzin (kg/l), Diesel (kg/l), Strommix (kg/kWh)
        
        **Plots**
        1. Äquivalenzverbrauch (kWh/100 km)  
        2. CO₂ (g/km)  
        3. Kosten (€/100 km)
        
        **Standardannahmen**
        - CO₂-Faktoren: Benzin 2,31 kg/l, Diesel 2,65 kg/l; Strommix 0,33 kg/kWh (330 g/kWh).
        - Heizwerte: Benzin 8,9 kWh/l, Diesel 9,7 kWh/l.
        - Preise (Startwerte): Benzin 1,70 €/l, Diesel 1,60 €/l, Strom 0,50 €/kWh. 
          (ADAC: Q4/2024 ca. E5 ~1,72 €/l, E10 ~1,67 €/l, Diesel ~1,59 €/l – nutze bei Bedarf genauere 12M-Durchschnitte.)
        """
    )

    with st.sidebar:
        st.header("Einstellungen")
        km_total = st.slider("Gesamt-km", min_value=1000, max_value=100000, step=500, value=19000)

        st.subheader("Hybrid (BMW 330e)")
        hyb_l_per_100 = st.slider("Benzin l/100 km", min_value=0.0, max_value=12.0, step=0.1, value=5.2)
        hyb_kwh_per_100 = st.slider("Strom kWh/100 km", min_value=0.0, max_value=25.0, step=0.1, value=8.2)

        st.subheader("Diesel (BMW 330d)")
        diesel_l_per_100 = st.slider("Diesel l/100 km", min_value=5.0, max_value=7.0, step=0.1, value=6.0)

        st.subheader("BEV (BMW i4/ VW ID.7)")
        bev_kwh_per_100 = st.slider("Strom kWh/100 km (BEV)", min_value=14.0, max_value=28.0, step=0.1, value=20.0)

        st.subheader("Energiepreise")
        price_petrol = st.slider("Benzin €/l", min_value=1.3, max_value=2.2, step=0.01, value=1.70)
        price_diesel = st.slider("Diesel €/l", min_value=1.3, max_value=2.2, step=0.01, value=1.60)
        price_kwh = st.slider("Strom €/kWh", min_value=0.2, max_value=0.8, step=0.01, value=0.50)

        st.subheader("CO₂-Faktoren")
        co2_petrol = st.slider("Benzin kg/l", min_value=2.2, max_value=2.4, step=0.01, value=2.31)
        co2_diesel = st.slider("Diesel kg/l", min_value=2.5, max_value=2.8, step=0.01, value=2.65)
        co2_grid = st.slider("Strom kg/kWh", min_value=0.05, max_value=0.6, step=0.01, value=0.33)

    df = compute_totals(
        km_total,
        hyb_l_per_100,
        hyb_kwh_per_100,
        diesel_l_per_100,
        bev_kwh_per_100,
        price_petrol,
        price_diesel,
        price_kwh,
        co2_petrol,
        co2_diesel,
        co2_grid,
    )

    st.subheader("Kennzahlen")
    st.dataframe(df)

    chart_order = [
        ("Hybrid (BMW 330e)", "Hybrid"),
        ("Diesel (BMW 330d)", "Diesel"),
        ("BEV (BMW i4/ VW ID.7)", "BEV"),
    ]

    cols = st.columns(3)
    charts = [
        ("Energie (kWh/100km)", "Äquivalenzverbrauch"),
        ("CO2 (g/km)", "CO₂-Emissionen"),
        ("Kosten/100km (€)", "Kosten pro 100 km"),
    ]

    for col, (column, title) in zip(cols, charts):
        order_labels = [idx for idx, _ in chart_order]
        short_labels = dict(chart_order)
        chart_data = (
            df.loc[order_labels, [column]]
            .rename(index=short_labels)
            .reset_index()
            .rename(columns={"index": "Antrieb"})
        )
        col.subheader(title)
        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X("Antrieb:N", sort=None, axis=alt.Axis(labelAngle=0, title=None)),
                y=alt.Y(f"{column}:Q", axis=alt.Axis(title=column)),
                tooltip=["Antrieb", column],
            )
            .properties(height=320)
        )
        col.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    main()
