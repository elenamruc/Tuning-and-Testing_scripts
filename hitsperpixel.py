import ROOT
import sys
import os
from array import array

# Function to draw and save the histogram with an optional additional axis
def draw_Hitsperpixel(prim, canvas, output_folder, name_suffix=""):
    """
    Draws the histogram of hits per pixel on the specified canvas and saves the image
    """
    # Clear the title of the histogram, if any
    prim.SetTitle("") 
    
    # Activate the canvas to draw the histogram and set the margins
    canvas.cd() 
    canvas.SetLeftMargin(0.1)
    canvas.SetRightMargin(0.17)
    
    
    # Draw the histogram using a color scale to represent the hits per pixel
    prim.Draw("COLZ") 

    # Set the title for the Z-axis
    prim.SetZTitle("Hits Per Pixel")
    # Configure the size and font of the axis titles
    prim.SetZTitle("Hits Per Pixel")
    prim.GetXaxis().SetTitleSize(34)
    prim.GetXaxis().SetTitleFont(43)
    prim.GetYaxis().SetTitleSize(34)
    prim.GetYaxis().SetTitleFont(43)
    prim.GetZaxis().SetTitleSize(34)  
    prim.GetZaxis().SetTitleFont(43) 
    prim.GetZaxis().SetTitleOffset(1.8)
    prim.GetXaxis().SetLabelSize(0.04)  
    prim.GetYaxis().SetLabelSize(0.04) 
    prim.GetZaxis().SetLabelSize(0.04)
     
    # Draw and position the stats box
    ROOT.gPad.Update()
    
    # Adjust the position of the color bar
    palette = prim.GetListOfFunctions().FindObject("palette")
    if palette:
        palette.SetX1NDC(0.83)
        palette.SetX2NDC(0.87)
        palette.SetY1NDC(canvas.GetBottomMargin())
        palette.SetY2NDC(1 - canvas.GetTopMargin()) 
        
    # Locate and adjust the stats box
    stats = prim.GetListOfFunctions().FindObject("stats")
    if stats:
        top_margin = canvas.GetTopMargin()
        right_margin = canvas.GetRightMargin()
        stats_height = 0.15
        stats_width = 0.2    
        # Calculate positions based on margins
        x1_ndc = 1 - right_margin - stats_width
        x2_ndc = 1 - right_margin
        y2_ndc = 1 - top_margin
        y1_ndc = y2_ndc - stats_height

	# Apply the calculated positions to the stats box
        stats.SetY1NDC(y1_ndc-0.06)
        stats.SetY2NDC(y2_ndc-0.03)
        stats.SetX1NDC(x1_ndc-0.03)
        stats.SetX2NDC(x2_ndc-0.03)

        canvas.Modified() 

    # Update the canvas before saving to ensure all elements are drawn
    canvas.Update()

    # Save canvas as an image
    file_path = os.path.join(output_folder, f"{prim.GetName()}{name_suffix}.png")
    canvas.SaveAs(file_path)
    print(f"Histogram saved: {file_path}")
    
def draw_missing_prob(prim, masked_hist, canvas, output_folder, name_suffix="", masked_pixels = False):
    """
    Draws histograms based on masked and unmasked pixel data from the hits per pixel map. It also handles the creation of different histograms depending on the hits registered.
    """
    # Get dimensions of the primary histogram
    nx, ny = prim.GetNbinsX(), prim.GetNbinsY()
    

    # Create a histogram to hold filtered values
    filtered_hist = ROOT.TH2F("filtered_hist", "", nx, 0, nx, ny, 0, ny)

    # Fill the histogram with values, marking masked ones differently if specified 
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            content = prim.GetBinContent(ix, iy)
            if masked_hist.GetBinContent(ix, iy) != 0:  # Check if pixel is masked
                # Set a distinct value for masked pixel
                filtered_hist.SetBinContent(ix, iy, 2000)
            else:
                # Copy value to the filtered histogram
                filtered_hist.SetBinContent(ix, iy, content)
           
    bx, by = filtered_hist.GetNbinsX(), filtered_hist.GetNbinsY()

    # Create additional histograms for visualization
    missing = ROOT.TH2F("missing", "", bx, 0, bx, by, 0, by)
    problematic = ROOT.TH2F("problematic", "", bx, 0, bx, by, 0, by)
    if masked_pixels:
        masked = ROOT.TH2F("masked", "", bx, 0, bx, by, 0, by)
    
    canvas.SetTitle("Bump-Bonds")
    
    # Set visual styles for histograms
    missing.SetFillColor(ROOT.kRed)  # Red for missing pixels
    problematic.SetFillColor(ROOT.kBlue)  # Blue for problematic pixels
    if masked_pixels:
        masked.SetFillColor(ROOT.kGreen+2)  
        masked.SetStats(0)
        masked.GetXaxis().SetTitle("Columns")
        masked.GetYaxis().SetTitle("Rows")
    
    # Populate histograms based on z-values
    missing_count = 0
    problematic_count = 0
    masked_count = 0
    missing_positions = []
    problematic_positions = []
    
    for binX in range(1, bx + 1):
        for binY in range(1, by + 1):
            z = filtered_hist.GetBinContent(binX, binY)
            if z < 100:
                # Pixels that detect less than 100 hits:
                missing.SetBinContent(binX, binY, 1)
                missing_count += 1
                missing_positions.append((binX, binY))
            elif 100 <= z < 1000:
                # Pixels that detect hits between 100 and 1000:
                problematic.SetBinContent(binX, binY, 1)
                problematic_count += 1
                problematic_positions.append((binX, binY))
            elif z == 2000 and masked_pixels:
                # Masked pixels
                masked.SetBinContent(binX, binY, 1)
                masked_count += 1
            else:
                continue
    # Disable the stats box to clean up the plot
    missing.SetStats(0)
    problematic.SetStats(0)
    
    # Setup the plot titles
    missing.GetXaxis().SetTitle("Columns")
    missing.GetYaxis().SetTitle("Rows")
    problematic.GetXaxis().SetTitle("Columns")
    problematic.GetYaxis().SetTitle("Rows")

    # Add a legend to explain the color coding
    canvas.cd()
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.1)

    missing.Draw("BOX")  
    problematic.Draw("BOX SAME")  
    legend = ROOT.TLegend(0.17, 0.17, 0.375, 0.3)
    legend.SetTextSize(0.034) 
    legend.SetMargin(0.08)
    legend.AddEntry(missing, "Missing bumps", "f")
    legend.AddEntry(problematic, "Problematic bumps", "f")
    
    if masked_pixels:
        masked.Draw("BOX SAME")
        legend.AddEntry(masked, "Masked pixels", "f")
    legend.Draw()
    

    # Update the canvas and save the output file
    canvas.Modified()
    canvas.Update()
    file_path = os.path.join(output_folder, f"filtered{name_suffix}_withoutT.png")
    canvas.SaveAs(file_path)
    print(f"Filtered histogram saved: {file_path}")
    print(f"Masked pixels count: {masked_count}")
    print(f"Missing entries count: {missing_count}")
    print(f"Problematic entries count: {problematic_count}")
    
    # Write canvas to the ROOT file
    canvas_name = f"Filtered{name_suffix}Canvas"
    canvas.Write(canvas_name)
    print(f"Canvas written to ROOT file as {canvas_name}")
    print(f"Histogram name filtered{name_suffix}")
    
    # Save the bad bump-bonds position in a .txt
    Bump_bonds_Xray = os.path.join(output_folder, f"Bump_bonds_Xray.txt")

    with open(Bump_bonds_Xray, 'w') as f:
        f.write("Missing Positions:\n")
        for pos in missing_positions:
            f.write(f"{pos[0]}, {pos[1]}\n")
        f.write("\nProblematic Positions:\n")
        for pos in problematic_positions:
            f.write(f"{pos[0]}, {pos[1]}\n")  
    
    return missing_positions, problematic_positions
    
def draw_z_histograms(prim, masked_hist, canvas, output_folder, log_scale=False):
    """
    Hits per pixel distribution
    """

    # Retrieve the number of bins in the x and y directions
    n_bins_x = prim.GetNbinsX()
    n_bins_y = prim.GetNbinsY()

    # Create a list to store z-values (number of hits per pixel)
    z_values_all = []
    z_values_unmasked = []
    for i in range(1, n_bins_x + 1):
        for j in range(1, n_bins_y + 1):
            z_value = prim.GetBinContent(i, j)
            if masked_hist.GetBinContent(i, j) == 0:  # Check if the pixel is not masked
                z_values_unmasked.append(z_value)
            z_values_all.append(z_value)
            
        
    # Loop through both sets of Z values to create histograms
    for z_values, label in [(z_values_all, "all"), (z_values_unmasked, "unmasked")]:
        hist_z_values = ROOT.TH1F(f"hist_z_values_{label}", ";Hits per Pixel;Entries",
                                  100, min(z_values), max(z_values))
        canvas.SetTitle("HitsPerPixel1D")

        # Fill the histogram
        for z in z_values:
            hist_z_values.Fill(z)

        # Set the line width for better visibility
        hist_z_values.SetLineWidth(2)

        # Draw the histogram
        canvas.cd()
        if log_scale:
            canvas.SetLogy(1)  # Set logarithmic scale if specified
        else:
            canvas.SetLogy(0)

        hist_z_values.Draw("HIST")
        canvas.Update()

        # Locate and adjust the statistics box
        stats = hist_z_values.GetListOfFunctions().FindObject("stats")
        if stats:
            top_margin = canvas.GetTopMargin()
            right_margin = canvas.GetRightMargin()
            stats_height = 0.15
            stats_width = 0.2    
            # Calculate positions based on margins
            x1_ndc = 1 - right_margin - stats_width
            x2_ndc = 1 - right_margin
            y2_ndc = 1 - top_margin
            y1_ndc = y2_ndc - stats_height

            # Apply the calculated positions to the stats box
            stats.SetY1NDC(y1_ndc-0.03)
            stats.SetY2NDC(y2_ndc-0.03)
            stats.SetX1NDC(x1_ndc-0.03)
            stats.SetX2NDC(x2_ndc-0.03)
            
        canvas.Modified()
        canvas.Update()
    
        # Save the histogram image
        image_name = f"z_histogram_{label}_{('log' if log_scale else 'linear')}.png"
        image_path = os.path.join(output_folder, image_name)
        canvas.SaveAs(image_path)
        print(f"Histogram image saved at: {image_path}")
        
        # Write the current state of the canvas to the ROOT file
        canvas_name = f"ZHistogram{label.capitalize()}{'Log' if log_scale else 'Linear'}Canvas"
        canvas.Write(canvas_name)
        print(f"Canvas written to ROOT file as {canvas_name}")

def save_histograms_png(root_file, masked_file):
    # Open ROOT File
    file = ROOT.TFile.Open(root_file, "READ")
    masked_file2 = ROOT.TFile.Open(masked_file, "READ")
    # Extract the histogram representing masked pixels
    masked_hist = masked_file2.Get("Masked Pixels Map")
    
    if not file.IsOpen():
        print(f"Could not open file {root_file}")
        return

    # Prepare output folder
    base_name = os.path.basename(root_file)
    root_name = os.path.splitext(base_name)[0]
    output_folder = os.path.join(os.getcwd(), root_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    

    # Prepare the canvas
    canvas = ROOT.TCanvas("canvas", "canvas", 1150, 800)
    canvas.SetBottomMargin(0.12)

    # Open a ROOT file to save all canvas outputs
    output_root_file = ROOT.TFile(os.path.join(output_folder, "Occ_and_hits.root"), "RECREATE")		

    # Function to process directories and TCanvas objects
    def process_directory(directory, rute=""):
        for key in directory.GetListOfKeys():
            obj = key.ReadObj()
            if obj.IsA().InheritsFrom(ROOT.TDirectory.Class()):
                new_path = f"{rute}/{obj.GetName()}" if rute else obj.GetName()
                result = process_directory(obj, new_path)
                if result:
                    return result
            elif obj.IsA().InheritsFrom(ROOT.TCanvas.Class()) and obj.GetName() == "D_B(0)_O(0)_H(0)_PixelAlive_Chip(15)":
                print(f"Found Canvas: {obj.GetName()}")
                for prim in obj.GetListOfPrimitives():
                    if prim.InheritsFrom(ROOT.TH1.Class()):
                        print(f"Found Histogram: {prim.GetName()}")
                        return prim
        return None 
        
    # Function to process directories and TCanvas objects
    prim = process_directory(file)    
    if prim:
        prim.SetLineWidth(2)
        prim.GetXaxis().SetTitleOffset(1)
        prim.GetYaxis().SetTitleOffset(1.8)
        prim.Scale(1e7)
        # Draw and save the hits per pixel histogram
        draw_Hitsperpixel(prim, canvas, output_folder, "_Hist")
        canvas.Write("HitsPerPixelCanvas")
        # Clone the primary histogram to use for the custom drawings
        prim_clone_for_masked = prim.Clone("prim_clone_for_masked")
        prim_clone_for_unmasked = prim.Clone("prim_clone_for_unmasked")
         # Draw and save the custom histograms for masked and unmasked pixels
        draw_missing_prob(prim_clone_for_masked, masked_hist, canvas, output_folder, "_colors_mp", masked_pixels = True)
        missing_positions, problematic_positions = draw_missing_prob(prim_clone_for_unmasked, masked_hist, canvas, output_folder, "_colors", masked_pixels = False)
        
        # Draw and save the z-value histograms in both linear and log scale
        #draw_z_histograms(prim_clone_for_unmasked, canvas, output_folder, log_scale=False)
        draw_z_histograms(prim_clone_for_unmasked, masked_hist, canvas, output_folder, log_scale=False)
        #draw_z_histograms(prim_clone_for_unmasked, canvas, output_folder, log_scale=True)
        draw_z_histograms(prim_clone_for_unmasked, masked_hist, canvas, output_folder, log_scale=True)
        

    else:
        print("No valid histogram was found.")
    file.Close()
    masked_file2.Close()
    output_root_file.Close()  # Ensure to close the ROOT file after all operations
    

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py file1.root file2.root")
        sys.exit(1)
    root_file = sys.argv[1]
    masked_file = sys.argv[2]
    save_histograms_png(root_file, masked_file)

