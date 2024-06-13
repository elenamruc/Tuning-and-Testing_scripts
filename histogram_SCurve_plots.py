import ROOT
import sys
import os

def format_stats_box(prim, fit_function, perform_fit, title, newaxis_title):
    """
    Creates and formats the statistics box for histograms, allowing for optional fitting information.
    """
    # Choose the position of the title box based on whether fitting is performed
    if perform_fit:
        title_box = ROOT.TPaveText(0.65, 0.81, 0.88, 0.85, "NDC")
    else:
        title_box = ROOT.TPaveText(0.60, 0.81, 0.83, 0.85, "NDC")

    # Set properties of the title box
    title_box.AddText(title)
    title_box.SetFillColor(0)  # Transparent background
    title_box.SetBorderSize(1)  # Size of the border
    title_box.SetTextAlign(22)  # Center alignment of the text
    titleode_box.SetTextFont(42)  # Font style
    title_box.SetFillStyle(1001)  # Solid fill style
    title_box.Draw()

    # Choose the position of the statistics box based on whether fitting is performed
    if perform_fit:
        stats_box = ROOT.TPaveText(0.65, 0.62, 0.88, 0.81, "NDC")
    else:
        stats_box = ROOT.TPaveText(0.60, 0.70, 0.83, 0.81, "NDC")

    # Set properties of the statistics box
    stats_box.SetFillColor(0)  # Transparent background
    stats_box.SetBorderSize(1)  # Size of the border
    stats_box.SetFillStyle(1001)  # Solid fill style
    stats_box.SetTextAlign(12)  # Left alignment of the text
    stats_box.SetTextFont(42)  # Font style

    # Add statistical information to the box based on the type of histogram
    if perform_fit and newaxis_title == "Noise":
        stats_box.AddText("Entries                                       {:.0f}".format(prim.GetEntries()))
        stats_box.AddText("Mean                                           {:.2f}".format(prim.GetMean()))
        stats_box.AddText("Std Dev                                         {:.2f}".format(prim.GetStdDev()))
        stats_box.AddText("Mean (fit)                      {:.3f} #pm {:.3f}".format(fit_function.GetParameter(1), fit_function.GetParError(1)))
        stats_box.AddText("Std Dev (fit)                     {:.3f} #pm {:.3f}".format(fit_function.GetParameter(2), fit_function.GetParError(2)))
        stats_box.AddText("Chi^2/ndf (fit)                          {:.2f}/{:d}".format(fit_function.GetChisquare(), fit_function.GetNDF()))
        
    elif perform_fit and newaxis_title == "Threshold":
        stats_box.AddText("Entries                                       {:.0f}".format(prim.GetEntries()))
        stats_box.AddText("Mean                                          {:.2f}".format(prim.GetMean()))
        stats_box.AddText("Std Dev                                        {:.2f}".format(prim.GetStdDev()))
        stats_box.AddText("Mean (fit)                     {:.3f} #pm {:.3f}".format(fit_function.GetParameter(1), fit_function.GetParError(1)))
        stats_box.AddText("Std Dev (fit)                   {:.3f} #pm {:.3f}".format(fit_function.GetParameter(2), fit_function.GetParError(2)))
        stats_box.AddText("Chi^2/ndf (fit)                       {:.2f}/{:d}".format(fit_function.GetChisquare(), fit_function.GetNDF()))
    elif perform_fit == False and newaxis_title == "Noise": 
        stats_box.AddText("Entries            {:.0f}".format(prim.GetEntries()))
        stats_box.AddText("Mean                 {:.2f}".format(prim.GetMean()))
        stats_box.AddText("Std Dev               {:.2f}".format(prim.GetStdDev()))
    elif perform_fit == False and newaxis_title == "Threshold": 
        stats_box.AddText("Entries            {:.0f}".format(prim.GetEntries()))
        stats_box.AddText("Mean               {:.2f}".format(prim.GetMean()))
        stats_box.AddText("Std Dev             {:.2f}".format(prim.GetStdDev()))
    else:
        stats_box.AddText("Entries            {:.0f}".format(prim.GetEntries()))
        stats_box.AddText("Mean                 {:.2f}".format(prim.GetMean()))
        stats_box.AddText("Std Dev             {:.2f}".format(prim.GetStdDev()))    


    return title_box, stats_box
    
    
def draw_and_save_histogram(prim, canvas, output_folder, newaxis_title, x1_pos, x2_pos, xe_pos, ye_pos, is_log=False, name_suffix="", add_axis=False, x_cut=None, perform_fit=False, colz=False):
    """
    Draws and saves a histogram to a specified path, with options for logarithmic scale, axis customization, and fitting.
    """
    canvas.cd()  # Set the current canvas
    ROOT.gStyle.SetOptStat(0)  # Disable the default statistics box
    ROOT.gStyle.SetOptFit(0)  # Disable the default fit box
    canvas.SetLogy(is_log)  # Set logarithmic scale if specified

    # Set margins for the canvas to ensure all elements are visible
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.1)

    # Set the title and axis labels
    prim.SetTitle("")  # Clear the default title
    if newaxis_title == "SCurve":
        prim.SetXTitle("Charge (#DeltaVCal)")  # Specific label for SCurve
    else:
        prim.SetXTitle(f"{newaxis_title} (#DeltaVCal)")  # Generic label
        

    # Set label sizes for readability
    prim.GetXaxis().SetLabelSize(0.04)
    prim.GetYaxis().SetLabelSize(0.04)   

    # Draw histogram with color map if specified
    if colz:
        prim.GetZaxis().SetLabelSize(0.04)  # Label size for the Z-axis
        prim.SetZTitle("Number of Pixels")  # Z-axis title
        canvas.SetRightMargin(0.15)  # Adjust right margin for Z-axis labels
        canvas.SetTopMargin(0.12)  # Adjust top margin
        canvas.SetLogz(1)  # Set logarithmic scale for Z-axis
        prim.Draw("COLZ")  # Draw with color map
    else:
        prim.Draw("HIST")  # Draw as a histogram

    # If a cut-off for the X-axis is provided, apply it
    if x_cut is not None:
        prim.GetXaxis().SetRangeUser(x_cut[0], x_cut[1])
    else:
        # Use the full range of the X-axis
        prim.GetXaxis().SetRangeUser(prim.GetXaxis().GetXmin(), prim.GetXaxis().GetXmax())
  
    # Perform fitting if specified
    if perform_fit:
        if newaxis_title == "Noise":
            #fit_result = prim.Fit("gaus", "S+", "", 19.5, 27.5) #1000 electrons
            fit_result = prim.Fit("gaus", "S+", "", 19, 27)  #2000 electrons
        elif newaxis_title == "Threshold":
            #fit_result = prim.Fit("gaus", "S", "", 140, 240) #1000 electrons
            fit_result = prim.Fit("gaus", "S+", "", 360, 440) #2000 electrons
        fit_function = prim.GetFunction("gaus")
        fit_function.SetLineColor(ROOT.kRed)
        fit_function.Draw("same") 

    canvas.Update() # Update the canvas to reflect changes

    # Configure title and axis properties    
    prim.GetXaxis().SetTitleSize(34)
    prim.GetXaxis().SetTitleFont(43)
    prim.GetYaxis().SetTitleSize(34)
    prim.GetYaxis().SetTitleFont(43)
    prim.GetZaxis().SetTitleSize(34) 
    prim.GetZaxis().SetTitleFont(43) 
    prim.GetZaxis().SetTitleOffset(1.8)
    prim.GetXaxis().SetLabelSize(0.04) 
    prim.GetYaxis().SetLabelSize(0.04)  

    # Draw and display the title and statistics boxes
    title, stats_box = format_stats_box(prim, fit_function if perform_fit else None, perform_fit, f"{newaxis_title} w7-24", newaxis_title)
    title.Draw()
    stats_box.Draw()
    canvas.Modified()
    canvas.Update()

    # Add an additional axis if specified
    if add_axis:
        canvas.Update() 
        # Adjust y-position based on log scale
        y_pos = ROOT.gPad.GetUymax() if not is_log else 10**ROOT.gPad.GetUymax()
        # Create the second axis, conversion to electrons
        new_axis = ROOT.TGaxis(x1_pos, y_pos, x2_pos, y_pos, xe_pos, ye_pos, 510, "-L")
        new_axis.SetTitle(f"Charge (electrons)")
        new_axis.SetLabelFont(43)
        new_axis.SetLabelSize(30)
        new_axis.SetTitleFont(43)
        new_axis.SetTitleSize(30)
        new_axis.SetTitleOffset(1.5)
        new_axis.Draw()
        
    canvas.Update()

    # Save the histogram to a file
    file_path = os.path.join(output_folder, f"{prim.GetName()}{name_suffix}_final.png")
    canvas.SaveAs(file_path) # Save the canvas as a PNG file
    print(f"Histogram saved: {file_path}") # Print confirmation message


def save_histograms_png(root_file):
    # Open ROOT File
    file = ROOT.TFile.Open(root_file, "READ")
    if not file.IsOpen():
        print(f"Could not open file {root_file}")
        return

    # Prepare output folder
    base_name = os.path.basename(root_file)
    root_name = os.path.splitext(base_name)[0]
    output_folder = os.path.join(os.getcwd(), root_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ROOT.gStyle.SetTitleSize(25, "xy")
    ROOT.gStyle.SetTitleFont(43, "xy")
    ROOT.gStyle.SetLabelSize(20, "xy")
    ROOT.gStyle.SetLabelFont(43, "xy")

    # Prepare the canvas
    canvas = ROOT.TCanvas("canvas", "canvas", 1150, 800)
    canvas.SetBottomMargin(0.12)

    # Function to process directories and TCanvas objects
    def process_directory(directory, rute=""):
        for key in directory.GetListOfKeys():
            obj = key.ReadObj()
            if obj.IsA().InheritsFrom(ROOT.TDirectory.Class()):
                new_path = f"{rute}/{obj.GetName()}" if rute else obj.GetName()
                process_directory(obj, new_path)
            elif obj.IsA().InheritsFrom(ROOT.TCanvas.Class()) and obj.GetName() in ["D_B(0)_O(0)_H(0)_Noise1D_Chip(15)", "D_B(0)_O(0)_H(0)_Threshold1D_Chip(15)", "D_B(0)_O(0)_H(0)_SCurves_Chip(15)"]:
                for prim in obj.GetListOfPrimitives():
                    if prim.InheritsFrom(ROOT.TH1.Class()):
                        prim.SetLineWidth(2)
                        prim.GetXaxis().SetTitleOffset(1)
                        prim.GetYaxis().SetTitleOffset(1.9)
                        
                        x1 = prim.GetXaxis().GetXmin()
                        x2 = prim.GetXaxis().GetXmax()
                            
                        if obj.GetName() == "D_B(0)_O(0)_H(0)_Noise1D_Chip(15)":
                            draw_and_save_histogram(prim, canvas, output_folder, "Noise", x1, x2, 0, 959.534, is_log=False, name_suffix="", add_axis=False)
                            draw_and_save_histogram(prim, canvas, output_folder, "Noise", 0, 50, 0, 239.884, is_log=False, name_suffix="_short_", add_axis=False, x_cut=(0, 50), perform_fit=True)
                            # Draw and save log scale
                            #canvas.SetLogy(1)
                            #draw_and_save_histogram(prim, canvas, output_folder, "Noise", "Noise1D", x1, x2, 0, 959.534, is_log=True, name_suffix="_log_with_axis", add_axis=True, x_cut=None)
                            #draw_and_save_histogram(prim, canvas, output_folder, "Noise", "Noise1D", 0, 50, 0, 239.884, is_log=True, name_suffix="_log_with_axis_short", add_axis=True, x_cut=(0, 50))
                            #draw_and_save_histogram(prim, canvas, output_folder, "Noise", "Noise1D", 0, 50, 0, 239.884, is_log=True, name_suffix="_log_with_axis_short_fit", add_axis=True, x_cut=(0, 50), perform_fit=True)
                            #canvas.SetLogy(0)  # Reset log scale
                        
                        elif obj.GetName() == "D_B(0)_O(0)_H(0)_SCurves_Chip(15)":                            
                            draw_and_save_histogram(prim, canvas, output_folder, "SCurve", x1, x2, 64, 4853.34, is_log=False, name_suffix="", add_axis=True)
                            draw_and_save_histogram(prim, canvas, output_folder, "SCurve", x1, x2, 64, 4853.34, is_log=False, name_suffix="colz", add_axis=True, colz=True)

                            
                        if obj.GetName() == "D_B(0)_O(0)_H(0)_Threshold1D_Chip(15)":
                            draw_and_save_histogram(prim, canvas, output_folder, "Threshold", x1, x2, 64, 4944.96, is_log=False, name_suffix="", add_axis=False)
                            draw_and_save_histogram(prim, canvas, output_folder, "Threshold", 300, 500, 1528.288, 2504.48, is_log=False, name_suffix="_short_", add_axis=False, x_cut=(300, 500), perform_fit=True) #2000 electrons
                            #draw_and_save_histogram(prim, canvas, output_folder, "Threshold", 100, 300, 552.096, 1528.28, is_log=False, name_suffix="_short_", add_axis=False, x_cut=(100, 300), perform_fit=True) #1000 electrons
                            # Draw and save log scale
                            #canvas.SetLogy(1)
                            #draw_and_save_histogram(prim, canvas, output_folder, "Threshold", "Threshold1D", x1, x2, 64, 4880.96, is_log=True, name_suffix="_log_with_axis", add_axis=True, x_cut=None)
                            #draw_and_save_histogram(prim, canvas, output_folder, "Threshold", "Threshold1D", 100, 300, 552.096, 1528.28, is_log=True, name_suffix="_log_with_axis_short", add_axis=True, x_cut=(100, 300))
                            #draw_and_save_histogram(prim, canvas, output_folder, "Threshold", "Threshold1D",  100, 300, 552.096, 1528.28, is_log=True, name_suffix="_log_with_axis_short_fit", add_axis=True, x_cut=(100, 300), perform_fit=True)
                            #canvas.SetLogy(0)  # Reset log scale
                            
                            
    process_directory(file)
    file.Close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py file.root")
        sys.exit(1)
    for root_file in sys.argv[1:]:
        print(f"Processing {root_file}")
        save_histograms_png(root_file) 
