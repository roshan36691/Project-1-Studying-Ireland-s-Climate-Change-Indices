import seaborn as sns
from faicons import icon_svg

# Import data from shared.py
from shared import app_dir, df_germany,df_ireland
from shiny import reactive
from shiny.express import input, render, ui
import matplotlib.pyplot as plt


ui.page_opts(title="Climate Predictions", fillable=True)
with ui.sidebar(title="Filter controls"):
    ui.input_selectize(  
    "selectize_1",  
    "Select a country:",  
    {"1A": "Ireland", "1B": "Germany"},  )

    ui.input_checkbox_group(
        "regions",
        "Select a region:",
        ["north-central", "north-east", "north-west","south-central","south-east","south-west"],
        selected=["north-central"]
    )

    ui.input_selectize(  
    "selectize_3",  
    "Select a parameter:",  
    {"3A": "Percipitation", "3B": "Temperature"},  )

    ui.input_slider("slider", "Period:", min=1825, max=2023, value=[1825, 2010])
    @render.text
    def value():
        return f"{input.slider()}"

with ui.layout_columns():
    with ui.card(full_screen=True):
        @reactive.Calc
        def filtered_df():
            selected_country = input.selectize_1()
            if selected_country == "1A":  # Ireland
                df = df_ireland
            elif selected_country == "1B":  # Germany
                df = df_germany

            selected_regions = input.regions()
            if not selected_regions:
                return df  # Return the entire DataFrame if no regions are selected
            filtered = df[df["Region"].isin(selected_regions)]
            return filtered

        @render.plot
        def length_depth():
            # Get the filtered DataFrame based on the selected regions
            df_filtered = filtered_df()

            if df_filtered.empty:
                plt.figure(figsize=(11, 7))
                plt.text(0.5, 0.5, 'No data available for the selected regions.', 
                        horizontalalignment='center', verticalalignment='center',
                        fontsize=15, color='red')
                plt.axis('off')
                plt.tight_layout()
                return plt.gcf()

            # Get the selected parameter from the dropdown
            selected_param = input.selectize_3()

            # Get the selected year range from the slider
            year_range = input.slider()
            start_year, end_year = year_range

            # Filter the DataFrame based on the selected year range
            df_filtered = df_filtered[(df_filtered['Year'] >= start_year) & (df_filtered['Year'] <= end_year)]

            plt.figure(figsize=(12, 7))
            colors = plt.get_cmap('tab10')
            color_list = colors(range(len(input.regions())))

            wet_label_added = False
            dry_label_added = False
            high_temp_label_added = False
            low_temp_label_added = False

            threshold_percentage = 0.2  # Example threshold percentage for extreme weather conditions

            for i, region in enumerate(input.regions()):
                region_data = df_filtered[df_filtered['Region'] == region]

                if selected_param == "3A":  # If Precipitation is selected
                    baseline = region_data['Avg Precipitation'].mean()  # Calculate baseline for the region
                    plt.plot(region_data['Year'], region_data['Avg Precipitation'], marker='o', color=color_list[i], label=region)
                    plt.axhline(y=baseline, color='grey', linestyle='--', label=f'{region} Avg: {baseline:.2f}')

                    # Define thresholds for precipitation
                    extreme_wet_threshold = baseline * (1 + threshold_percentage)
                    extreme_dry_threshold = baseline * (1 - threshold_percentage)

                    # Highlight extreme wet years
                    wet_years = region_data[region_data['Avg Precipitation'] > extreme_wet_threshold]
                    plt.scatter(wet_years['Year'], wet_years['Avg Precipitation'], color='blue', marker='^', label='Extreme Wet Years' if not wet_label_added else "", s=100)
                    wet_label_added = True

                    # Highlight extreme dry years
                    dry_years = region_data[region_data['Avg Precipitation'] < extreme_dry_threshold]
                    plt.scatter(dry_years['Year'], dry_years['Avg Precipitation'], color='red', marker='v', label='Extreme Dry Years' if not dry_label_added else "", s=100)
                    dry_label_added = True
                    plt.ylabel('Avg Max Precipitation')

                elif selected_param == "3B":  # If Temperature is selected
                    baseline = region_data['Avg Max Temp'].mean()  # Calculate baseline for temperature in the region
                    plt.plot(region_data['Year'], region_data['Avg Max Temp'], marker='o', color=color_list[i], label=region)
                    plt.axhline(y=baseline, color='grey', linestyle='--', label=f'{region} Temp Avg: {baseline:.2f}')

                    # Define thresholds for high and low temperatures
                    high_threshold = baseline * (1 + threshold_percentage)
                    low_threshold = baseline * (1 - threshold_percentage)

                    # Highlight temperatures above the high threshold
                    high_temps = region_data[region_data['Avg Max Temp'] > high_threshold]
                    plt.scatter(high_temps['Year'], high_temps['Avg Max Temp'], color='red', marker='^', label='High Temp (>20%)' if not high_temp_label_added else "", s=100)
                    high_temp_label_added = True

                    # Highlight temperatures below the low threshold
                    low_temps = region_data[region_data['Avg Max Temp'] < low_threshold]
                    plt.scatter(low_temps['Year'], low_temps['Avg Max Temp'], color='blue', marker='v', label='Low Temp (<-20%)' if not low_temp_label_added else "", s=100)
                    low_temp_label_added = True

                    plt.ylabel('Avg Temperature')

            param_mapping = {"3A": "Precipitation", "3B": "Temperature"}
            plt.title(f'Year vs. {param_mapping[selected_param]} by Region')
            plt.xlabel('Year')
            plt.legend(title="Regions")
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()

            return plt.gcf()
ui.include_css(app_dir / "styles.css")




