import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px # Import plotly for charting
import plotly.graph_objects as go # Import graph objects for more control if needed

# Load data
@st.cache_data
def load_data():
    # Assuming Data_2025.xlsx is in the same directory as app.py
    url = "Data_2025.xlsx"
    return pd.read_excel(url, sheet_name="data", engine='openpyxl')

df = load_data()

# Resolve potential column naming issues for robustness
def get_column_safe(df, name_options):
    for name in name_options:
        if name in df.columns:
            return name
    return None

unit_name_col = get_column_safe(df, ["Unit name", "Unit Name"])
region_col = get_column_safe(df, ["Region"])
year_col = get_column_safe(df, ["Year"])
quarter_col = get_column_safe(df, ["Quarter"])
recovery_col = get_column_safe(df, ["Recovery type", "Recovery Type", "Recovery_type"])
size_col = get_column_safe(df, ["Unit size", "Unit Size"])
brand_col = get_column_safe(df, ["Brand name", "Brand"])
logo_col = get_column_safe(df, ["Brand logo", "Brand Logo"])
unit_photo_col = get_column_safe(df, ["Unit photo", "Unit Photo", "Unit Photo Name"]) # Added common names for unit photo column
internal_height_col = get_column_safe(df, ["Internal Height (Supply Fan)", "Internal Height Supply Fan"]) # Added for specific chart placement check

# --- Chart specific column names ---
# Store resolved X and Y coordinate column names as pairs
coord_col_pairs = []
for i in range(1, 6): # For X1, Y1 to X5, Y5
    # Add more options for column names if there are variations in your Excel file
    x_col_name = get_column_safe(df, [f"X{i}", f"x{i}", f"X{i}_coord", f"x{i}_coord"])
    y_col_name = get_column_safe(df, [f"Y{i}", f"y{i}", f"Y{i}_coord", f"y{i}_coord"])
    if x_col_name and y_col_name: # Only add if both X and Y for a point are found
        coord_col_pairs.append((x_col_name, y_col_name))
    else:
        # Provide a warning if expected coordinate columns are not found in the DataFrame
        # This helps in debugging missing columns in the Excel file
        if not x_col_name:
            st.sidebar.warning(f"Warning: Coordinate column 'X{i}' not found in data. Chart may be incomplete.")
        if not y_col_name:
            st.sidebar.warning(f"Warning: Coordinate column 'Y{i}' not found in data. Chart may be incomplete.")


# Main layout filters for the comparison interface
st.title("Technical Data Comparison")

# Create two columns for side-by-side selection and display
col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    # Dropdown menus for the first comparison set
    selected_year1 = st.selectbox("Year", sorted(df[year_col].dropna().unique()), key="year1")
    selected_quarter1 = st.selectbox("Quarter", sorted(df[quarter_col].dropna().unique()), key="quarter1")
    selected_region1 = st.selectbox("Region", sorted(df[region_col].dropna().unique()), key="region1")
    selected_brand1 = st.selectbox("Select Brand", sorted(df[brand_col].dropna().unique()), key="brand1")

    # Display Brand Logo for the first selection
    # Filter the DataFrame to get the logo path for the selected brand
    brand1_logo_path = df[df[brand_col] == selected_brand1][logo_col].iloc[0] if not df[df[brand_col] == selected_brand1].empty and logo_col else None
    if brand1_logo_path:
        try:
            # Open and resize the image, maintaining aspect ratio
            image1 = Image.open(f"images/{brand1_logo_path}")
            width1 = 150 # Desired fixed width in pixels
            height1 = int(image1.height * (width1 / image1.width)) # Calculate height to maintain aspect ratio
            image1 = image1.resize((width1, height1))
            st.image(image1, caption=f"Logo for {selected_brand1}") # Display the image with a caption
        except FileNotFoundError:
            st.warning(f"Brand logo image not found for {selected_brand1}: images/{brand1_logo_path}")
        except Exception as e:
            st.warning(f"Error loading brand logo for {selected_brand1}: {e}")
    else:
        st.write("No logo available for selected brand.")

    # Continue with other dropdowns for the first comparison set
    selected_unit1 = st.selectbox("Unit name", sorted(df[unit_name_col].dropna().unique()), key="unit1")
    selected_recovery1 = st.selectbox("Recovery type", sorted(df[recovery_col].dropna().unique()), key="recovery1")
    selected_size1 = st.selectbox("Unit size", sorted(df[size_col].dropna().unique()), key="size1")


with col_filter2:
    # Dropdown menus for the second comparison set
    selected_year2 = st.selectbox("Year", sorted(df[year_col].dropna().unique()), key="year2")
    selected_quarter2 = st.selectbox("Quarter", sorted(df[quarter_col].dropna().unique()), key="quarter2")
    selected_region2 = st.selectbox("Region", sorted(df[region_col].dropna().unique()), key="region2")
    selected_brand2 = st.selectbox("Select Brand", sorted(df[brand_col].dropna().unique()), key="brand2")

    # Display Brand Logo for the second selection
    brand2_logo_path = df[df[brand_col] == selected_brand2][logo_col].iloc[0] if not df[df[brand_col] == selected_brand2].empty and logo_col else None
    if brand2_logo_path:
        try:
            image2 = Image.open(f"images/{brand2_logo_path}")
            width2 = 150 # Desired fixed width in pixels
            height2 = int(image2.height * (width2 / image2.width)) # Calculate height to maintain aspect ratio
            image2 = image2.resize((width2, height2))
            st.image(image2, caption=f"Logo for {selected_brand2}")
        except FileNotFoundError:
            st.warning(f"Brand logo image not found for {selected_brand2}: images/{brand2_logo_path}")
        except Exception as e:
            st.warning(f"Error loading brand logo for {selected_brand2}: {e}")
    else:
        st.write("No logo available for selected brand.")

    # Continue with other dropdowns for the second comparison set
    selected_unit2 = st.selectbox("Unit name", sorted(df[unit_name_col].dropna().unique()), key="unit2")
    selected_recovery2 = st.selectbox("Recovery type", sorted(df[recovery_col].dropna().unique()), key="recovery2")
    selected_size2 = st.selectbox("Unit size", sorted(df[size_col].dropna().unique()), key="size2")

# Filter dataframes based on selected criteria for both comparison sets
filtered_df1 = df[
    (df[year_col] == selected_year1) &
    (df[quarter_col] == selected_quarter1) &
    (df[region_col] == selected_region1) &
    (df[brand_col] == selected_brand1) &
    (df[unit_name_col] == selected_unit1) &
    (df[recovery_col] == selected_recovery1) &
    (df[size_col] == selected_size1)
]

filtered_df2 = df[
    (df[year_col] == selected_year2) &
    (df[quarter_col] == selected_quarter2) &
    (df[region_col] == selected_region2) &
    (df[brand_col] == selected_brand2) &
    (df[unit_name_col] == selected_unit2) &
    (df[recovery_col] == selected_recovery2) &
    (df[size_col] == selected_size2)
]

# Display Unit Photos after dropdowns and before the comparison table
st.subheader("Unit Photo")
col_photo1, col_photo2 = st.columns(2) # Create columns for side-by-side unit photos

with col_photo1:
    # Get the unit photo path for the first selection
    unit_photo_path1 = filtered_df1[unit_photo_col].values[0] if not filtered_df1.empty and unit_photo_col and unit_photo_col in filtered_df1.columns else None
    if unit_photo_path1:
        try:
            # Open and display the unit photo
            unit_image1 = Image.open(f"images/{unit_photo_path1}")
            st.image(unit_image1, caption=f"{selected_unit1} Photo")
        except FileNotFoundError:
            st.warning(f"Unit photo image not found for {selected_unit1}: images/{unit_photo_path1}")
        except Exception as e:
            st.warning(f"Error loading unit photo for {selected_unit1}: {e}")
    else:
        st.write("No unit photo available for this selection.")

with col_photo2:
    # Get the unit photo path for the second selection
    unit_photo_path2 = filtered_df2[unit_photo_col].values[0] if not filtered_df2.empty and unit_photo_col and unit_photo_col in filtered_df2.columns else None
    if unit_photo_path2:
        try:
            # Open and display the unit photo
            unit_image2 = Image.open(f"images/{unit_photo_path2}")
            st.image(unit_image2, caption=f"{selected_unit2} Photo")
        except FileNotFoundError:
            st.warning(f"Unit photo image not found for {selected_unit2}: images/{unit_photo_path2}")
        except Exception as e:
            st.warning(f"Error loading unit photo for {selected_unit2}: {e}")
    else:
        st.write("No unit photo available for this selection.")

st.markdown("---") # Add a horizontal separator line for better visual separation

# Chart Generation Logic (moved outside the parameter loop for consistent placement)
if not filtered_df1.empty and not filtered_df2.empty:
    chart_data = []
    
    # Check if all 5 coordinate pairs were found during initial column resolution
    if len(coord_col_pairs) != 5:
        st.warning("Not all 5 coordinate pairs (X1-X5, Y1-Y5) were identified in the data. Chart may not display correctly.")

    # Check if coordinate columns exist and have non-NaN values for each brand
    can_plot_brand1 = True
    if not filtered_df1.empty: # Ensure filtered_df1 is not empty before checking
        for x_name, y_name in coord_col_pairs:
            if x_name not in filtered_df1.columns or pd.isna(filtered_df1[x_name].values[0]) or \
               y_name not in filtered_df1.columns or pd.isna(filtered_df1[y_name].values[0]):
                can_plot_brand1 = False
                st.info(f"Incomplete coordinate data for {selected_brand1}. Chart may not include this brand.")
                break # Exit loop if any coordinate is missing/NaN
    else:
        can_plot_brand1 = False # No data for filtered_df1

    can_plot_brand2 = True
    if not filtered_df2.empty: # Ensure filtered_df2 is not empty before checking
        for x_name, y_name in coord_col_pairs:
            if x_name not in filtered_df2.columns or pd.isna(filtered_df2[x_name].values[0]) or \
               y_name not in filtered_df2.columns or pd.isna(filtered_df2[y_name].values[0]):
                can_plot_brand2 = False
                st.info(f"Incomplete coordinate data for {selected_brand2}. Chart may not include this brand.")
                break # Exit loop if any coordinate is missing/NaN
    else:
        can_plot_brand2 = False # No data for filtered_df2


    # Process data for the first selection if all coordinates are present and not NaN
    if can_plot_brand1:
        for i, (x_name, y_name) in enumerate(coord_col_pairs):
            chart_data.append({
                'X_coord': filtered_df1[x_name].values[0] / 20.0,
                'Y_coord': filtered_df1[y_name].values[0] / 20.0,
                'Source': selected_brand1,
                'Point_Order': i + 1 # Point order 1 to 5
            })
    

    # Process data for the second selection if all coordinates are present and not NaN
    if can_plot_brand2:
        for i, (x_name, y_name) in enumerate(coord_col_pairs):
            chart_data.append({
                'X_coord': filtered_df2[x_name].values[0] / 20.0,
                'Y_coord': filtered_df2[y_name].values[0] / 20.0,
                'Source': selected_brand2,
                'Point_Order': i + 1 # Point order 1 to 5
            })
    

    if chart_data: # Only attempt to plot if some data is gathered
        st.subheader("Unit Geometry Comparison") # New subheader for the chart
        chart_df = pd.DataFrame(chart_data)

        # Sort by Point_Order to ensure lines are drawn correctly for rectangles
        chart_df = chart_df.sort_values(by=['Source', 'Point_Order'])
        
        # Create the Plotly chart
        fig = px.line(chart_df,
                      x="X_coord",
                      y="Y_coord",
                      color="Source",
                      line_group="Source", # Group lines by source
                      markers=True, # Show markers at data points
                      title="Scaled Rectangle Dimensions (1:20 mm)")
        
        # Update layout for better visualization
        fig.update_layout(
            xaxis_title="X Coordinate (mm)",
            yaxis_title="Y Coordinate (mm)",
            hovermode="x unified",
            legend_title_text="Brand",
            xaxis_constrain="domain", # Keeps aspect ratio better
            yaxis_constrain="domain", # Keeps aspect ratio better
            showlegend=True
        )
        
        # Ensure the aspect ratio is equal if it's a drawing
        fig.update_yaxes(scaleanchor="x", scaleratio=1)

        st.plotly_chart(fig, use_container_width=True)
    else: # If chart_data is empty after checks
        st.warning("No complete coordinate data (X1-X5, Y1-Y5) found for selected units to generate the geometry chart. Please ensure data is present and valid for both selections.")


    # Now, display the comparison table
    st.subheader("Comparison Table") # Main header for the comparison table

    # Define columns for the table header
    col1, col2, col3 = st.columns([2, 3, 3]) # Adjust column widths as needed
    with col1:
        st.markdown("**Parameter**") # Header for the parameter column
    with col2:
        st.markdown(f"**{selected_brand1}**") # Header for the first brand's values
    with col3:
        st.markdown(f"**{selected_brand2}**") # Header for the second brand's values

    # List of columns to be excluded from the comparison table display as per user request
    excluded_cols = [
        brand_col, logo_col, unit_photo_col, year_col, quarter_col, region_col,
        unit_name_col, recovery_col, size_col, internal_height_col # Exclude chart placement column
    ]
    # Add all resolved coordinate column names to the excluded list
    for x_name, y_name in coord_col_pairs:
        excluded_cols.append(x_name)
        excluded_cols.append(y_name)


    # Iterate through all columns in the original DataFrame to display comparison values
    for col in df.columns:
        # Only display columns that are not in the excluded list
        if col not in excluded_cols:
            # Get values for each column for both filtered dataframes
            val1 = filtered_df1[col].values[0] if col in filtered_df1.columns else "-"
            val2 = filtered_df2[col].values[0] if col in filtered_df2.columns else "-" 
            
            # Create columns for each row of the comparison table
            row_col1, row_col2, row_col3 = st.columns([2, 3, 3])
            with row_col1:
                st.write(col) # Display the parameter name
            with row_col2:
                st.write(val1) # Display the value for the first brand
            with row_col3:
                st.write(val2) # Display the value for the second brand
else:
    # Display a warning if data is missing for comparison
    st.warning("One of the selected combinations has no data to display for comparison. Please adjust your selections.")
