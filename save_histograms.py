import ROOT 
import sys  
import os   

def process_directory(directory, rute=""):
    """
    Recursively searches a ROOT directory and its subdirectories for a histogram with a specific name.
    """
    for key in directory.GetListOfKeys():
        obj = key.ReadObj()
        if obj.IsA().InheritsFrom(ROOT.TDirectory.Class()):
            # If the object is a directory, recursively process it
            new_path = f"{rute}/{obj.GetName()}" if rute else obj.GetName()
            process_directory(obj, new_path)
        elif obj.IsA().InheritsFrom(ROOT.TCanvas.Class()):
            # If the object is a canvas, process it
            process_canvas(obj)

def process_canvas(canvas):
    """
    Process a TCanvas object and its primitives, such as histograms.
    """
    canvasName = canvas.GetName()

    # Iterate over the primitives of the canvas
    for prim in canvas.GetListOfPrimitives():
        if prim.InheritsFrom(ROOT.TH1.Class()):
            # If the primitive is a histogram, process it
            process_histogram(canvas, prim)

def process_histogram(canvas, prim):
    """
    Process a histogram within a TCanvas object. It draws the histogram, adjusts settings, and saves it as an image.
    """
    canvasName = canvas.GetName()
    name_histogram = prim.GetName()
    
    # Remove the title of the histogram
    prim.SetTitle("")
    
    if name_histogram != "D_B(0)_O(0)_H(0)_Noise2D_Chip(15)" and name_histogram != "D_B(0)_O(0)_H(0)_Threshold2D_Chip(15)" and name_histogram != "D_B(0)_O(0)_H(0)_ThrNoise2D_Chip(15)":
        return
    # Prepare the canvas for Threshold vs Noise in this case
    canvas = ROOT.TCanvas("Threshold vs Noise w7-24", "canvas", 1150, 800)
    canvas.SetLeftMargin(0.11)
    canvas.SetRightMargin(0.15)   

    # Draw the histogram
    prim.Draw()

    if canvasName == "D_B(0)_O(0)_H(0)_PixelAlive_Chip(15)" or canvasName == "D_B(0)_O(0)_H(0)_Noise2D_Chip(15)" or canvasName == "D_B(0)_O(0)_H(0)_Threshold2D_Chip(15)" or "D_B(0)_O(0)_H(0)_ThrNoise2D_Chip(15)":
        # For a specific canvas, adjust the color axis and draw statistics
        y_min = prim.GetMinimum()
        y_max = prim.GetMaximum()
        canvas.SetLogz(0)
        prim.SetZTitle("Number of Pixels") 

        prim.GetXaxis().SetTitleSize(34)
        prim.GetXaxis().SetTitleFont(43)
        prim.GetYaxis().SetTitleSize(34)
        prim.GetYaxis().SetTitleFont(43)
        prim.GetZaxis().SetTitleSize(34)
        prim.GetZaxis().SetTitleFont(43)
        prim.GetXaxis().SetLabelSize(0.04) 
        prim.GetYaxis().SetLabelSize(0.04) 
        prim.GetZaxis().SetLabelSize(0.04)  
        prim.GetZaxis().SetTitleOffset(1.8)
        
        
        
        prim.Draw("COLZ")
        prim.GetZaxis().SetRangeUser(y_min, y_max)
        
        # Ajust the palette position
        palette = prim.GetListOfFunctions().FindObject("palette")
        if palette:
            palette.SetX1NDC(0.85)
            palette.SetX2NDC(0.89)
        canvas.Update()
    
    stats = prim.GetListOfFunctions().FindObject("stats")
    if  canvasName == "D_B(0)_O(0)_H(0)_Occ1D_Chip(15)" or canvasName == "D_B(0)_O(0)_H(0)_Threhsold_Chip(15)" or canvasName == "D_B(0)_O(0)_H(0)_ToT1D_Chip(15)" or canvasName == "D_B(0)_O(0)_H(0)_TDAC1D_Chip(15)":
        stats.SetX1NDC(0.68)
        stats.SetY1NDC(0.71)
        stats.SetX2NDC(0.88)
        stats.SetY2NDC(0.86)

    else:
        stats.SetX1NDC(0.15)
        stats.SetY1NDC(0.71)
        stats.SetX2NDC(0.35)
        stats.SetY2NDC(0.88)
    stats.Draw()
    canvas.Update()

    # Save the histogram as an image
    exit_path = os.path.join(output_folder, f"{name_histogram}_withoutT.png")
    canvas.SaveAs(exit_path)
    print(f"Histogram saved: {exit_path}")

    canvas.SetLogz(0)
    canvas.SetLogy(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py file.root")
        sys.exit(1)
    
    for root_file in sys.argv[1:]:
        print(f"Processing {root_file}")
        file = ROOT.TFile.Open(root_file, "READ")
        if not file.IsOpen():
            print(f"Could not open file {root_file}")
            continue
        
        base_name = os.path.basename(root_file)
        root_name = os.path.splitext(base_name)[0]
        output_folder = os.path.join(os.getcwd(), root_name)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        process_directory(file)
        file.Close()







