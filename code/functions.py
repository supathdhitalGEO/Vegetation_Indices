#%%
import geemap
import pandas as pd
from geopandas import gpd   
import ee
import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from rasterio.plot import show
from pathlib import Path
from skimage.transform import resize
from matplotlib_scalebar.scalebar import ScaleBar
#%%
#to save the data collection
def save_data(out_dir, image, filename, ROI):
    file_dir = out_dir/filename
    basename = filename.split('.')[0].split('_')[0]
    if basename =='landsat':
        geemap.download_ee_image(image, filename = file_dir, scale=30, region=ROI, crs='EPSG:4326')
        
    elif basename == 'sentinel':
        geemap.download_ee_image(image, filename = file_dir, scale=10, region=ROI, crs='EPSG:4326')
        
    elif basename == 'LULC':
        geemap.download_ee_image(image, filename = file_dir, scale= 10, region=ROI, crs='EPSG:4326')
    
# %%
def get_eesupported_roi(shp_file):
    shp = gpd.read_file(shp_file)
    shp = shp.to_crs(epsg=4326)
    roi_geom = shp.geometry.values[0]
    roi_geojson = roi_geom.__geo_interface__
    roi_ee = ee.Geometry(roi_geojson)
    return roi_ee

#%%
def get_lulc(roi_ee):
    dataset = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterDate('2022-04-01', '2022-07-01')
    # Clip the image with the region of interest.
    dw_image = ee.Image(dataset.mosaic()).clip(roi_ee)
    classification = dw_image.select('label')
    return classification

#%%
# Define a constant for the L parameter used in SAVI calculation
L = 0.5

def read_raster(raster_path, data_dir):
    with rasterio.open(raster_path) as src:
        profile = src.profile
        basename = os.path.basename(raster_path).split('.')[0]
        basename_split = basename.split('_')[0]
        
        if basename_split == 'landsat':
            red = src.read(4).astype(np.float32)
            nir = src.read(5).astype(np.float32)
            blue = src.read(2).astype(np.float32)
            green = src.read(3).astype(np.float32)

            # Replace NaN values with mean of each band
            red = np.where(np.isnan(red), np.nanmean(red), red)
            nir = np.where(np.isnan(nir), np.nanmean(nir), nir)
            blue = np.where(np.isnan(blue), np.nanmean(blue), blue)
            green = np.where(np.isnan(green), np.nanmean(green), green)
            
            print(f"Calculation of NDVI, EVI, NDWI, and SAVI in progress for: {basename}")
            
            # NDVI Calculation
            ndvi = (nir - red) / (nir + red)
            
            # Calculate EVI
            evi = 2.5 * ((nir - red) / (nir + 6 * red - 7.5 * blue + 1))
            
            # Calculate NDWI
            ndwi = (green - nir) / (green + nir)
            
            # Calculate SAVI
            savi = ((nir - red) * (1 + L)) / (nir + red + L)
            
            # Create metric folders inside the current folder if they don't exist
            metric_dirs = ['NDVI', 'EVI', 'NDWI', 'SAVI']
            for metric in metric_dirs:
                metric_dir = Path(data_dir) / metric
                os.makedirs(metric_dir, exist_ok=True)
            
            # Save NDVI, EVI, NDWI, and SAVI raster files
            ndvi_path = Path(data_dir) / 'NDVI' / f'{basename}NDVI.tif'
            evi_path = Path(data_dir) / 'EVI' / f'{basename}EVI.tif'
            ndwi_path = Path(data_dir) / 'NDWI' / f'{basename}NDWI.tif'
            savi_path = Path(data_dir) / 'SAVI' / f'{basename}SAVI.tif'
            
            # Call the save_raster function to save the raster files
            save_raster(ndvi_path, ndvi, src)
            save_raster(evi_path, evi, src)
            save_raster(ndwi_path, ndwi, src)  
            save_raster(savi_path, savi, src)  

def save_raster(output_path, data, src):
    profile = src.profile
    profile.update(dtype=rasterio.float32, count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(data.astype(rasterio.float32), 1)
        print(f"Raster file saved at: {output_path}")

def process_all_folders(main_folder):
    for root, dirs, files in os.walk(main_folder):
        for file in files:
            if file.endswith('.tif'):
                raster_path = Path(root) / file
                print(f'Processing {raster_path}...')
                read_raster(raster_path, root)
# %%
import os
import re
import matplotlib.pyplot as plt
import rasterio
from skimage.transform import resize
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Enable LaTeX font rendering
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']

def plot_rasters_with_custom_titles(data_dir, custom_titles, colorbar_label, output):
    # Get all .tif files in the directory
    tif_files = [os.path.join(data_dir, file) for file in os.listdir(data_dir) if file.endswith('.tif')]

    # Extract the Landsat number from the filename and sort the files accordingly
    tif_files.sort(key=lambda x: int(re.search(r'(\d+)', os.path.basename(x)).group()))

    # Compute the global min and max values across all images
    global_min = float('inf')
    global_max = float('-inf')
    for tif_file in tif_files:
        dataset = rasterio.open(tif_file)
        raster_data = dataset.read(1)
        global_min = min(global_min, raster_data.min())
        global_max = max(global_max, raster_data.max())
        dataset.close()

    # Plotting the rasters
    num_images = len(tif_files)
    cols = 2  
    rows = (num_images + 1) // cols  
    target_size = (512, 512) 

    fig, axs = plt.subplots(rows, cols, figsize=(6, 3 * rows), gridspec_kw={'hspace': 0.3, 'wspace': 0.1})

    for i, tif_file in enumerate(tif_files):
        row = i // cols
        col = i % cols
        ax = axs[row, col] if rows > 1 else axs[col]

        dataset = rasterio.open(tif_file)
        raster_data = dataset.read(1)
        bounds = dataset.bounds
        extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
        
        # Resize raster data to target size
        raster_resized = resize(raster_data, target_size, mode='reflect', anti_aliasing=True)
        
        # Use the global min and max for consistent color mapping
        img = ax.imshow(raster_resized, cmap='terrain', extent=extent, vmin=global_min, vmax=global_max)
        ax.set_title(rf'{custom_titles[i]}', fontsize=10)
        
        # Set x and y labels
        ax.set_xlabel('Longitude', fontsize=9)
        if col == 0: 
            ax.set_ylabel('Latitude', fontsize=9)
        else:
            ax.set_ylabel('')
            ax.set_yticklabels([]) 
        
        ax.yaxis.set_tick_params(rotation=90)
        
        # Adjust tick label sizes
        ax.tick_params(axis='both', which='major', labelsize=7)
        ax.tick_params(axis='both', which='minor', labelsize=7) 

        # Calculate the approximate scale in meters at the center latitude
        center_latitude = (bounds.top + bounds.bottom) / 2
        meters_per_degree_lat, meters_per_degree_lon = degree_to_meters(center_latitude)
        mean_meters_per_degree = (meters_per_degree_lat + meters_per_degree_lon) / 2

        # Add scale bar 
        scalebar = ScaleBar(mean_meters_per_degree, units='m', dimension='si-length', 
                            location='lower right', pad=0.1, font_properties={'size': 7})
        ax.add_artist(scalebar)
        
        dataset.close()
        
        # Add a single color bar after the second image in each row
        if col == 1:
            cax = fig.add_axes([ax.get_position().x1 + 0.005, ax.get_position().y0, 0.015, ax.get_position().height])
            colorbar = plt.colorbar(img, cax=cax, orientation='vertical')
            colorbar.set_label(colorbar_label, rotation=90)
            colorbar.ax.tick_params(labelsize=7)
        
    # Save the plot
    plt.savefig(output, dpi=400, bbox_inches='tight')

    # Adjust layout
    plt.tight_layout()
    plt.show()

def degree_to_meters(latitude):
    # Approximation: 1 degree latitude ~ 111 km
    meters_per_degree = 111e3
    meters_per_degree_lon = meters_per_degree * np.cos(np.radians(latitude))
    return meters_per_degree, meters_per_degree_lon
#%%
import os
import rasterio
import numpy as np
import pandas as pd

def sample_raster_values(file_path):
    # Open the raster file
    src = rasterio.open(file_path)
    
    # Get raster dimensions
    rows, cols = src.shape
    
    # Read the entire raster data
    data = src.read(1)
    
    # Calculate overall statistics
    min_value = np.min(data)
    mean_value = np.mean(data)
    max_value = np.max(data)
    
    # Generate random pixel coordinates for sampling
    num_samples = 500
    random_indices = np.random.choice(rows * cols, num_samples, replace=False)
    random_rows = random_indices // cols
    random_cols = random_indices % cols
    
    # Extract pixel values
    sampled_values = data[random_rows, random_cols].tolist()
    
    # Ensure inclusion of overall statistics
    if min_value not in sampled_values:
        sampled_values[np.random.randint(num_samples)] = min_value
    
    if mean_value not in sampled_values:
        sampled_values[np.random.randint(num_samples)] = mean_value
    
    if max_value not in sampled_values:
        sampled_values[np.random.randint(num_samples)] = max_value
    
    # Close the raster file
    src.close()
    
    return sampled_values

def process_raster_directory(main_directory):
    # Iterate over vegetation index folders
    for veg_index_folder in os.listdir(main_directory):
        veg_index_path = os.path.join(main_directory, veg_index_folder)
        
        if os.path.isdir(veg_index_path):
            sampled_data = {}

            # Iterate over season subfolders
            for season_folder in os.listdir(veg_index_path):
                season_path = os.path.join(veg_index_path, season_folder)
                
                if os.path.isdir(season_path):
                    # Initialize lists to store sampled values for Landsat 8 and 9
                    landsat_8_values = []
                    landsat_9_values = []
                    
                    # Iterate over .tif files in the season folder
                    for filename in os.listdir(season_path):
                        if filename.endswith(".tif"):
                            file_path = os.path.join(season_path, filename)
                            
                            # Sample values for the raster file
                            sampled_values = sample_raster_values(file_path)
                            
                            # Store sampled values in the correct list based on Landsat number
                            if 'landsat_8' in filename.lower():
                                landsat_8_values.extend(sampled_values)
                            elif 'landsat_9' in filename.lower():
                                landsat_9_values.extend(sampled_values)
                    
                    # Add sampled values to the dictionary
                    sampled_data[f'{season_folder}_landsat_8'] = landsat_8_values
                    sampled_data[f'{season_folder}_landsat_9'] = landsat_9_values
            
            # Create a DataFrame
            df = pd.DataFrame(sampled_data)
            
            # Save to CSV in the vegetation index folder
            output_csv = os.path.join(veg_index_path, f'{veg_index_folder}_sampled.csv')
            df.to_csv(output_csv, index=False)
            
            print(f"Sampled values saved to {output_csv}")
# %%
