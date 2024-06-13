import ROOT
import sys
import os
import math
from ROOT import TLine
from array import array

# Obtain the path to the directory where execute_function.py is located
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the directory where hitsperpixel.py is located
# Move up two levels (to the directory 201-9B_practicas) and then down to Xray_20240405/Results
hitsperpixel_directory = os.path.abspath(os.path.join(current_home_directory, '..', '..', 'Xray_20240405', 'Results'))

# Add the directory to sys.path to allow importing from it
sys.path.append(hitsperpixel_directory)

# Import the draw_missing_prob function from the hitsperpixel module
from hitsperpixel import draw_missing_prob


# Set the statistics position box
def format_stats_box(prim, name):
    stats = prim.GetListOfFunctions().FindObject("stats")
    if stats:
        if name == "Noise":
            stats.SetX1NDC(0.68)
            stats.SetY1NDC(0.73)
            stats.SetX2NDC(0.88)
            stats.SetY2NDC(0.88)
        elif name == "Plot_2D":
            stats.SetX1NDC(0.15)
            stats.SetY1NDC(0.79)
            stats.SetX2NDC(0.30)
            stats.SetY2NDC(0.88)        
        elif name == "thrshift":
            stats.SetX1NDC(0.15)
            stats.SetY1NDC(0.71)
            stats.SetX2NDC(0.35)
            stats.SetY2NDC(0.88)
        else:
            stats.SetX1NDC(0.15)
            stats.SetY1NDC(0.73)
            stats.SetX2NDC(0.35)
            stats.SetY2NDC(0.88)
    else:
        print("No stats box found for this histogram.")
     
    
def process_directory(directory, histogram_name):
    """
    Recursively searches a ROOT directory and its subdirectories for a histogram with a specific name.
    """
    for key in directory.GetListOfKeys():
        obj = key.ReadObj()
        if obj.IsA().InheritsFrom(ROOT.TDirectory.Class()):
            # Recursive search in subdirectories
            result = process_directory(obj, histogram_name)
            if result:
                return result
        elif obj.IsA().InheritsFrom(ROOT.TCanvas.Class()):
            # Return the histogram if the name matches
            if obj.GetName() == histogram_name:
                for prim in obj.GetListOfPrimitives():
                    if prim.InheritsFrom(ROOT.TH1.Class()):
                        # Clone and rename the histogram to manipulate freely
                        cloned_hist = prim.Clone("w7-24")
                        return cloned_hist
    return None
    
import ROOT
from ROOT import TLine

def plot_vcal_difference(root_file1, root_file2, hist_name, name, output_file):
    """
    Compares two histograms from two ROOT files and plots the difference in Vcal values. Also, it collects the positions that meets the established conditions. 
    """
    # Open ROOT files
    file1 = ROOT.TFile.Open(root_file1, "READ")
    file2 = ROOT.TFile.Open(root_file2, "READ")

    # Process directories to get histograms
    hist1 = process_directory(file1, hist_name)
    hist2 = process_directory(file2, hist_name)

    # Check if histograms were successfully retrieved
    if not hist1 or not hist2:
        print("Histograms not found.")
        return

    # Get the number of bins in X and Y directions
    nx = hist1.GetNbinsX()
    ny = hist1.GetNbinsY()

    # Initialize histogram for the differences based on the type of data
    if name == "Noise":
        vcal_diff_hist = ROOT.TH1F(f"{name} Shift w7-24", "", 2000, -500, 500)  # Adjust range as needed
    elif name == "Threshold":
        vcal_diff_hist = ROOT.TH1F(f"{name} Shift w7-24", "", 2000, -1800, 1800)  # Adjust range as needed

    differences = []  # List to store the differences between histogram values
    positions = []  # List to store the positions (bin coordinates) meeting specific conditions

    # Iterate over all bins
    for x in range(1, nx + 1):
        for y in range(1, ny + 1):
            vcal1 = hist1.GetBinContent(x, y)
            vcal2 = hist2.GetBinContent(x, y)
            diff = vcal1 - vcal2
            vcal_diff_hist.Fill(diff)  # Fill the histogram for differences
            differences.append(diff)
            # Collect positions where the differences meet specified conditions
            if (-40 <= diff <= 40) and name == "Threshold":
                positions.append((x, y))
            if name == "Noise" and (-15 <= diff <= 15):
                positions.append((x, y))

    # Set titles for the axes of the difference histogram
    vcal_diff_hist.SetXTitle(f"{name} Shift (#DeltaVcal)")
    vcal_diff_hist.SetYTitle("Number of Pixels")

    # Configure and draw the histogram canvas
    canvas = ROOT.TCanvas("canvas", f"{name} Shift", 1150, 800)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.1)
    canvas.SetLogy()  # Logarithmic scale for the Y-axis
    vcal_diff_hist.SetLineWidth(2)

    # Set size and font for the histogram's axes titles and labels
    vcal_diff_hist.GetXaxis().SetTitleSize(34)
    vcal_diff_hist.GetXaxis().SetTitleFont(43)
    vcal_diff_hist.GetYaxis().SetTitleSize(34)
    vcal_diff_hist.GetYaxis().SetTitleFont(43)
    vcal_diff_hist.GetXaxis().SetLabelSize(0.04)
    vcal_diff_hist.GetYaxis().SetLabelSize(0.04)

    vcal_diff_hist.Draw()  # Draw the histogram on the canvas

    # Draw lines indicating the threshold range for the differences
    if name == "Noise":
        line1 = TLine(15, 0, 15, vcal_diff_hist.GetMaximum())
        line2 = TLine(-15, 0, -15, vcal_diff_hist.GetMaximum())
    elif name == "Threshold":
        line1 = TLine(40, 0, 40, vcal_diff_hist.GetMaximum())
        line2 = TLine(-40, 0, -40, vcal_diff_hist.GetMaximum())

    line1.SetLineColor(ROOT.kRed)
    line1.SetLineWidth(2)
    line1.Draw("same")
    line2.SetLineColor(ROOT.kRed)
    line2.SetLineWidth(2)
    line2.Draw("same")

    canvas.Update()  # Update the canvas to reflect all drawings
    format_stats_box(vcal_diff_hist, f"{name}")  # Format and display statistics box

    # Save the histogram image and write the canvas to the output ROOT file
    image_name = f"{name}_Shift_withoutT.png"
    canvas.SaveAs(image_name)
    print(f"Histogram image saved at: {image_name}")

    output_file.cd()
    canvas_name = f"{name}_Shift"
    canvas.Write(canvas_name)
    print(f"Canvas written to ROOT file as {canvas_name}")

    # Close the opened ROOT files
    file1.Close()
    file2.Close()

    return differences, positions

def plot_positions_2d(positions, name_position, output_file):
    """
    Creates and plots a 2D histogram to visualize the bad bump-bonds positions  
    """
    # Create a 2D histogram to visualize positions
    hist2d = ROOT.TH2F("Bad Bumps w7-24", "", 432, 0, 432, 336, 0, 336)
    
    # Fill the histogram with positions that meet the criteria
    for x, y in positions:
        hist2d.Fill(x, y)
    
    # Set titles for the axes
    hist2d.SetXTitle("Column")
    hist2d.SetYTitle("Row")
    hist2d.SetFillColor(ROOT.kRed)  # Set the fill color to red
    
    # Create a canvas for drawing the histogram
    canvas = ROOT.TCanvas("canvas2d", "Bad Bumps", 1150, 800)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.1)
  
    # Set size and font for the histogram's axes titles and labels
    hist2d.GetXaxis().SetTitleSize(34)
    hist2d.GetXaxis().SetTitleFont(43)
    hist2d.GetYaxis().SetTitleSize(34)
    hist2d.GetYaxis().SetTitleFont(43)
    hist2d.GetXaxis().SetLabelSize(0.04)  # Increase label size for the X-axis
    hist2d.GetYaxis().SetLabelSize(0.04)  # Increase label size for the Y-axis   
    
    # Draw the histogram using 'BOX' option to use color to represent bin content
    hist2d.Draw("BOX")
    canvas.Update()
    format_stats_box(hist2d, f"{name_position}")
    ROOT.gStyle.SetOptStat(11)  # Configure to show only the number of entries in the stats box  
    
    # Save the histogram image to a file
    image_name = f"BadBumps_Positions_withoutT.png"
    canvas.Save___as(image_name)
    print(f"Histogram image saved at: {image_name}")
        
    # Write the current state of the canvas to the ROOT file
    output_file.cd()
    canvas_name = f"BadBumps_Positions"
    canvas.Write(canvas_name)
    print(f"Canvas written to ROOT file as {canvas_name}")


def plot_threshold_noise_2d(threshold_differences, noise_differences, name, output_file):
    """
    Plots a 2D histogram to visualize the relationship between threshold and noise shifts.
    """
    # Create a 2D histogram with specified bin ranges and numbers
    vcal_diff_hist_2d = ROOT.TH2F("Threshold vs Noise Shift", "", 2000, -1800, 1800, 2000, -200, 200)

    # Fill the histogram with difference data
    for i in range(len(threshold_differences)):
        vcal_diff_hist_2d.Fill(threshold_differences[i], noise_differences[i])
        
    # Set titles for the axes
    vcal_diff_hist_2d.SetXTitle(f"Threshold Shift (#DeltaVcal)")
    vcal_diff_hist_2d.SetYTitle("Noise Shift (#DeltaVcal)")
    
    # Create a canvas for drawing the histogram
    canvas = ROOT.TCanvas("canvas2d", "2D Vcal Differences", 1150, 800)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.15)

    # Configure text size and font for the histogram axes
    vcal_diff_hist_2d.GetXaxis().SetTitleSize(34)
    vcal_diff_hist_2d.GetXaxis().SetTitleFont(43)
    vcal_diff_hist_2d.GetYaxis().SetTitleSize(34)
    vcal_diff_hist_2d.GetYaxis().SetTitleFont(43)
    vcal_diff_hist_2d.GetZaxis().SetTitleSize(34)
    vcal_diff_hist_2d.GetZaxis().SetTitleFont(43)
    vcal_diff_hist_2d.GetXaxis().SetLabelSize(0.04)
    vcal_diff_hist_2d.GetYaxis().SetLabelSize(0.04)
    vcal_diff_hist_2d.GetZaxis().SetLabelSize(0.04)

    # Draw the histogram using a color map
    vcal_diff_hist_2d.Draw("COLZ")
    
    # Set additional Z-axis title properties and draw the plot
    vcal_diff_hist_2d.GetZaxis().SetTitle("Number of Pixels")
    vcal_diff_hist_2d.GetZaxis().SetTitleOffset(1)
    
    # Update the canvas to display changes
    canvas.Update()
    format_stats_box(vcal_diff_hist_2d, f"{name}")  # Add a formatted statistics box
    
    # Save the histogram image
    image_name = f"Threshold_vs_Noise_Shift.png"
    canvas.SaveAs(image_name)
    print(f"Histogram image saved at: {image_name}")
        
    # Write the canvas to the output ROOT file
    output_file.cd()
    canvas_name = f"Threshold_vs_Noise_Shift"
    canvas.Write(canvas_name)
    print(f"Canvas written to ROOT file as {canvas_name}")


def load_positions_from_file():
    """
    Loads positions from a text file that are specified as x, y coordinates separated by commas.
    """
    # Relative path from the current script location to the .txt file
    relative_path = "../../Xray_20240405/Results/Run000010_NoiseScan/Bump_bonds_Xray.txt"
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), relative_path))

    positions = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Ensure that the line is not empty
                # Process the line as needed
                parts = line.strip().split(',')
                if len(parts) == 2:
                    x, y = int(parts[0].strip()), int(parts[1].strip())
                    positions.append((x, y))
    return positions


def compare_positions(positions_xrays, positions_fwd_reverse, name_position, output_file):
    """
    Compares positions from two sets (X-ray and Forward-Reverse bias method), visualizing common and unique positions in a 2D histogram.
    """
    # Create a histogram to hold all bump bond comparisons
    canvas = ROOT.TCanvas("canvas2d", "Comparison of Bump Bonds", 1150, 800)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.1)
    
    # Histogram settings
    nx, ny = 432, 336  # assuming max X and Y values from your data
    bump_bonds = ROOT.TH2F("Bump Bonds", "", nx, 0, nx, ny, 0, ny)
    bump_bonds.SetStats(0)  # Disable the stats box
    
    # Define sets for easy comparison
    set_xrays = set(positions_xrays)
    set_fwd_reverse = set(positions_fwd_reverse)

    # Find common and unique positions
    common_positions = set_xrays.intersection(set_fwd_reverse)
    unique_fwd_reverse = set_fwd_reverse - set_xrays
    unique_xrays = set_xrays - set_fwd_reverse

    # Fill the histogram with different colors for different categories
    count_common = 0
    count_fwd = 0
    count_xrays = 0
    for x, y in common_positions:
        bump_bonds.Fill(x, y, 3)  # Common positions in red
        count_common += 1

    for x, y in unique_fwd_reverse:
        bump_bonds.Fill(x, y, 2)  # Fwd_reverse only in blue
        count_fwd += 1

    for x, y in unique_xrays:
        bump_bonds.Fill(x, y, 1)  # Xrays only in green
        count_xrays += 1
      
    # Display counts for debug and analysis purposes  
    print(f"Common: {count_common}, Xrays: {count_xrays}, Fwd:{count_fwd}")

    # Configure color display for the histogram
    bump_bonds.GetZaxis().SetRangeUser(1,3)
    bump_bonds.GetZaxis().SetLabelColor(1)  # Set labels to be visible
    colors = [ROOT.kGreen, ROOT.kBlue, ROOT.kRed]  # Define a color array
    ROOT.gStyle.SetPalette(len(colors), array('i', colors))  # Set the palette to the defined colors


    bump_bonds.GetXaxis().SetTitleSize(34)
    bump_bonds.GetXaxis().SetTitleFont(43)
    bump_bonds.GetYaxis().SetTitleSize(34)
    bump_bonds.GetYaxis().SetTitleFont(43)
    bump_bonds.GetXaxis().SetLabelSize(0.04)  # Aumentar el tamaño de las etiquetas del eje X
    bump_bonds.GetYaxis().SetLabelSize(0.04)  # Aumentar el tamaño de las etiquetas del eje Y 

    bump_bonds.Draw("col")  # Draw as colored boxes
    # Configure histogram appearance and draw it
    bump_bonds.SetXTitle("Column")
    bump_bonds.SetYTitle("Row")

    # Add a legend to describe the color coding
    legend = ROOT.TLegend(0.17, 0.74, 0.48, 0.87)
    legend.SetTextSize(0.034) 
    legend.SetMargin(0.08)
    box_green = ROOT.TBox()
    box_blue = ROOT.TBox()
    box_red = ROOT.TBox()
    box_green.SetFillColor(ROOT.kGreen)
    box_blue.SetFillColor(ROOT.kBlue)
    box_red.SetFillColor(ROOT.kRed)
   
    legend.AddEntry(box_red, "Common Bump Bonds: 123", "f")
    legend.AddEntry(box_blue, "Fwd_Reverse Only: 8", "f")
    legend.AddEntry(box_green, "Xrays Only: 2", "f")
    legend.Draw()
    
    # Update the canvas and save the result
    canvas.Modified()
    canvas.Update()
    
    # Save the canvas to the output ROOT file
    image_name = f"{name_position}_Bump_Bonds_withoutT.png"
    canvas.SaveAs(image_name)
    print(f"Histogram image saved at: {image_name}")
        
    # Write the current state of the canvas to the ROOT file
    output_file.cd()
    canvas_name = f"{name_position}_Bump_Bonds"
    canvas.Write(canvas_name)
    print(f"Canvas written to ROOT file as {canvas_name}")    
    
    
def main():
    """
    Main function to execute the analysis, compare histograms, and visualize differences.
    """

    # Set the color palette and number of contours for drawing histograms
    ROOT.gStyle.SetPalette(ROOT.kRainBow)  # Set the color palette to Rainbow for visual clarity
    ROOT.gStyle.SetNumberContours(255)  # Increase the number of contours to enhance visual granularity

    # Create or open a ROOT file to store the results of the analysis    
    output_file = ROOT.TFile("Fwd-reverse.root", "RECREATE")
    if output_file.IsOpen():
        print("ROOT file opened successfully.")

        # Define the paths to the ROOT files containing the histograms
        root_file1_24 = "Run000001_SCurve.root"
        root_file2_24 = "Run000002_SCurve.root"

        # Check if histograms exist in the ROOT files
        name_noise = "D_B(0)_O(0)_H(0)_Noise1D_Chip(15)"
        name_thr = "D_B(0)_O(0)_H(0)_Threshold1D_Chip(15)"
        name_noise_2D = "D_B(0)_O(0)_H(0)_Noise2D_Chip(15)"
        name_thr_2D = "D_B(0)_O(0)_H(0)_Threshold2D_Chip(15)"
        name_scurve =  "D_B(0)_O(0)_H(0)_SCurves_Chip(15)"
        name_thrnoise = "D_B(0)_O(0)_H(0)_ThrNoise2D_Chip(15)"

        # Calculate the differences between corresponding histograms in different ROOT files
        threshold_differences, positions_threshold = plot_vcal_difference(root_file1_24, root_file2_24, name_thr_2D, "Threshold", output_file)
        noise_differences, positions_noise = plot_vcal_difference(root_file1_24, root_file2_24, name_noise_2D, "Noise", output_file)

        # Plot 2D histograms if differences were successfully calculated
        if threshold_differences and noise_differences:
            plot_threshold_noise_2d(threshold_differences, noise_differences, "thrshift", output_file)
        
        # Compare positions from threshold and noise differences
        positions_fwd_reverse = []
        for pos_thresh in positions_threshold:
            if pos_thresh in positions_noise:
                positions_fwd_reverse.append(pos_thresh)
        
        # Visualize positions that meet certain criteria in a 2D plot
        plot_positions_2d(positions_fwd_reverse, "Plot_2D", output_file)

        # Load positions from a file for comparison
        positions_xrays = load_positions_from_file()
        compare_positions(positions_xrays, positions_fwd_reverse, "Plot_2D", output_file)
    
        # Finalize by writing and closing the ROOT file
        output_file.Write()
        output_file.Close()
        print("ROOT file closed successfully.")
    else:
        print("Failed to open the ROOT file.")
  
  
if __name__ == "__main__":
    main()


