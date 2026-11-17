#ifndef _layers_h_
#define _layers_h_

#include "structures.h"

/******************************************************************************
 * \file layers.h
 * \brief Functions for truncating fracture polygons to layer boundaries.
 *
 * When layerConformingFractures is enabled, fractures assigned to a layer
 * are clipped to that layer's +Z and -Z boundaries using the same
 * Sutherland-Hodgman half-space clipping algorithm used in domainTruncation().
 *
 * Three modes are supported via the integer layerConformingFractures:
 *   0 - Disabled: fractures extend freely beyond layer boundaries.
 *   1 - Perfect conforming: fractures are clipped exactly at the layer boundary.
 *   2 - Soft conforming: fractures are clipped at the layer boundary + 2h,
 *       preserving a small overhang that maintains geometric intersections
 *       with fractures in the adjacent layer for flow connectivity.
 ******************************************************************************/

/*!
 * \brief Clips a polygon to the Z-boundaries of its assigned layer.
 *
 * Uses half-space clipping against the layer's upper (+Z) and lower (-Z)
 * boundaries. The fracture center is allowed to be placed anywhere within
 * the layer (as determined by randomTranslation), but the polygon vertices
 * are clipped so no part of the fracture extends outside the layer's Z range.
 *
 * This function is a no-op if:
 *   - \p layerIndex is 0 (fracture belongs to the full domain), or
 *   - \p layerConformingFractures is 0 (disabled).
 *
 * \param newPoly     Polygon to be clipped (modified in place).
 * \param layerIndex  1-based index into the global \c layers[] array.
 *                    Layer i occupies layers[(i-1)*2] to layers[(i-1)*2+1].
 * \return  false (0) - Polygon survived clipping with 3 or more vertices.
 *          true  (1) - Polygon was rejected (clipped to fewer than 3 vertices,
 *                      or was entirely outside the layer).
 */
bool layerTruncation(Poly &newPoly, int layerIndex);

#endif // _layers_h_
