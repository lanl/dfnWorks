module FEHM

import WriteVTK
import JLD

function parsefin(filename)
	lines = readlines(filename)
	result = Dict()
	result["title"] = strip(split(lines[2], ":")[2])
	result["time"] = parse(Float64, lines[3])
	result["nddp"] = parse(Int, split(lines[4])[1])
	i = 5
	while i <= length(lines)
		key = strip(lines[i])
		result[key] = Float64[]
		i += 1
		while i <= length(lines) && length(result[key]) < result["nddp"]
			append!(result[key], map(x->parse(Float64, x), split(lines[i])))
			i += 1
		end
	end
	return result
end

function writefin(findata, filename; writekeys=["saturation", "pressure", "no fluxes"])
	f = open(filename, "w")
	write(f, "written by FEHM.jl\n")
	write(f, "title:  $(findata["title"])\n")
	write(f, "   $(findata["time"])\n")
	write(f, "    $(findata["nddp"]) nddp")
	for k in writekeys
		write(f, "\n$k")
		for x in findata[k]
			write(f, "\n$x")
		end
	end
	close(f)
end

function readzone(filename)
	f = open(filename)
	lines = readlines(f)
	lines = map(chomp, lines)
	close(f)
	if !startswith(lines[1], "zone") && !startswith(lines[1], "zonn")
		error("zone/zonn file doesn't start with zone or zonn on the first line")
	end
	nnumlines = Int64[]
	for i = 1:length(lines)
		if contains(lines[i], "nnum")
			push!(nnumlines, i)
		end
	end
	zonenumbers = Array(Int64, length(nnumlines))
	for i = 1:length(nnumlines)
		zonenumbers[i] = parse(Int, split(lines[nnumlines[i] - 1])[1])
	end
	nodenumbers = Array(Array{Int64, 1}, length(nnumlines))
	for i = 1:length(nnumlines)
		nodenumbers[i] = Int64[]
		numnodes = parse(Int, lines[nnumlines[i] + 1])
		j = 2
		while(length(nodenumbers[i]) < numnodes)
			newnodes = map(x->parse(Int, x), split(lines[nnumlines[i] + j]))
			nodenumbers[i] = [nodenumbers[i]; newnodes]
			j += 1
		end
	end
	return zonenumbers, nodenumbers
end

function parsegeo(geofilename, docells=true)
	lines = readlines(geofilename)
	i = 1
	xs = Float64[]
	ys = Float64[]
	zs = Float64[]
	splitline = split(lines[1])
	if length(splitline) != 4
		error("only 3 dimensional meshes supported")
	end
	while length(splitline) == 4
		x = parse(Float64, splitline[2])
		y = parse(Float64, splitline[3])
		z = parse(Float64, splitline[4])
		push!(xs, x)
		push!(ys, y)
		push!(zs, z)
		i += 1
		splitline = split(lines[i])
	end
	if docells
		cells = Array(WriteVTK.MeshCell, length(lines) - i + 1)
		fourtoseven = 4:7
		for j = i:length(lines)
			splitline = split(lines[j])
			if splitline[3] != "tet"
				error("only tets supported")
			end
			ns = map(i->parse(Int, splitline[i]), fourtoseven)
			cells[j - i + 1] = WriteVTK.MeshCell(WriteVTK.VTKCellTypes.VTK_TETRA, ns)
		end
	else
		cells = Array(WriteVTK.MeshCell, 0)
	end
	return xs, ys, zs, cells
end

function avs2vtk(inpname, vtkname)
	xs, ys, zs, cells = parsegeo(geofilename)
	avslines = readlines(string(inpname))
	for i = 5:length(avslines)
		splitline = split(avslines[i])
		avsrootname = splitline[1]
		vtkfile = WriteVTK.vtk_grid(string(vtkname), xs, ys, zs, cells)
		WriteVTK.vtk_point_data(vtkfile, "Cr")
		WriteVTK.vtk_save(vtkfile)
	end
end

function avs2jld(geofilename, rootname, jldfilename; timefilter=t->true)
	rootdir = joinpath(split(rootname, "/")[1:end-1]...)
	xs, ys, zs, cells = parsegeo(geofilename, false)
	avslines = readlines(string(rootname, ".avs_log"))
	crdatas = Array{Float64, 1}[]
	times = Float64[]
	for i = 5:length(avslines)
		splitline = split(avslines[i])
		avsrootname = joinpath(rootdir, splitline[1])
		time = parse(Float64, splitline[2])
		if timefilter(time)
			push!(times, time)
			timedata = readdlm(string(avsrootname, "_con_node.avs"), skipstart=2)
			crdata = timedata[:, 2]
			push!(crdatas, crdata)
		end
	end
	JLD.save(jldfilename, "Cr", crdatas, "times", times, "xs", xs, "ys", ys, "zs", zs)
end

end

inpname = 
vtkname =
avs2vtk(inpname, vtkname)
