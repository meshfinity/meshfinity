# Modified from: https://github.com/AllenInstitute/TrimeshVtk/blob/main/trimesh_vtk/__init__.py

import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy
import numpy as np


def numpy_to_vtk_cells(mat):
    """function to convert a numpy array of integers to a vtkCellArray

    Parameters
    ----------
    mat : np.array
        MxN array to be converted

    Returns
    -------
    vtk.vtkCellArray
        representing the numpy array, has the same shaped cell (N) at each of the M indices

    """

    cells = vtk.vtkCellArray()

    # Seemingly, VTK may be compiled as 32 bit or 64 bit.
    # We need to make sure that we convert the trilist to the correct dtype
    # based on this. See numpy_to_vtkIdTypeArray() for details.
    isize = vtk.vtkIdTypeArray().GetDataTypeSize()
    req_dtype = np.int32 if isize == 4 else np.int64
    n_elems = mat.shape[0]
    n_dim = mat.shape[1]
    cells.SetCells(
        n_elems,
        numpy_to_vtkIdTypeArray(
            np.hstack((np.ones(n_elems)[:, None] * n_dim, mat))
            .astype(req_dtype)
            .ravel(),
            deep=1,
        ),
    )
    return cells


def numpy_rep_to_vtk(vertices, shapes, edges=None):
    """converts a numpy representation of vertices and vertex connection graph
      to a polydata object and corresponding cell array

    Parameters
    ----------
    vertices: a Nx3 numpy array of vertex locations
    shapes: a MxK numpy array of vertex connectivity
                       (could be triangles (K=3) or edges (K=2))

    Returns
    -------
    vtk.vtkPolyData
        a polydata object with point set according to vertices,
    vtkCellArray
        a vtkCellArray of the shapes

    """

    mesh = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(vertices, deep=1))
    mesh.SetPoints(points)

    cells = numpy_to_vtk_cells(shapes)
    if edges is not None:
        if len(edges) > 0:
            edges = numpy_to_vtk_cells(edges)
        else:
            edges = None

    return mesh, cells, edges


def graph_to_vtk(vertices, edges):
    """converts a numpy representation of vertices and edges
      to a vtkPolyData object

    Parameters
    ----------
    vertices: np.array
        a Nx3 numpy array of vertex locations
    edges: np.array
        a Mx2 numpy array of vertex connectivity
        where the values are the indexes of connected vertices

    Returns
    -------
    vtk.vtkPolyData
        a polydata object with point set according to vertices
        and edges as its Lines

    Raises
    ------
    ValueError
        if edges is not 2d or refers to out of bounds vertices

    """
    if edges.shape[1] != 2:
        raise ValueError("graph_to_vtk() only works on edge lists")
    if np.max(edges) >= len(vertices):
        msg = "edges refer to non existent vertices {}."
        raise ValueError(msg.format(np.max(edges)))
    mesh, cells, edges = numpy_rep_to_vtk(vertices, edges)
    mesh.SetLines(cells)
    return mesh


def trimesh_to_vtk(vertices, tris, graph_edges=None):
    """Return a `vtkPolyData` representation of a :obj:`TriMesh` instance

    Parameters
    ----------
    vertices : np.array
        numpy array of Nx3 vertex positions (x,y,z)
    tris: np.array
        numpy array of Mx3 triangle vertex indices (int64)
    graph_edges: np.array
        numpy array of Kx2 of edges to set as the vtkPolyData.Lines

    Returns
    -------
    vtk_mesh : vtk.vtkPolyData
        A VTK mesh representation of the mesh :obj:`trimesh.TriMesh` data

    Raises
    ------
    ValueError:
        If the input trimesh is not 3D
        or tris refers to out of bounds vertex indices

    """

    if tris.shape[1] != 3:
        raise ValueError("trimesh_to_vtk() only works on 3D TriMesh instances")
    if np.max(tris) >= len(vertices):
        msg = "edges refer to non existent vertices {}."
        raise ValueError(msg.format(np.max(tris)))
    mesh, cells, edges = numpy_rep_to_vtk(vertices, tris, graph_edges)
    mesh.SetPolys(cells)
    if edges is not None:
        mesh.SetLines(edges)

    return mesh


def vtk_cellarray_to_shape(vtk_cellarray, ncells):
    """Turn a vtkCellArray into a numpyarray of a fixed shape
    assumes your cell array has uniformed sized cells

    Parameters
    ----------
    vtk_cellarray : vtk.vtkCellArray
        a cell array to convert
    ncells: int
        how many cells are in array

    Returns
    -------
    np.array
        cellarray, a ncells x K array of cells, where K is the
        uniform shape of the cells.  Will error if cells are not uniform

    """
    cellarray = vtk_to_numpy(vtk_cellarray)
    cellarray = cellarray.reshape(ncells, int(len(cellarray) / ncells))
    return cellarray[:, 1:]


def vtk_to_points_tris(vtk_poly_data):
    points = vtk_to_numpy(vtk_poly_data.GetPoints().GetData())
    ntris = vtk_poly_data.GetNumberOfPolys()
    tris = vtk_cellarray_to_shape(vtk_poly_data.GetPolys().GetData(), ntris)
    return points, tris
