#include <stdio.h>
#include <search.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "FuncDef.h"
#include <unistd.h>


struct posit3d
/*! structure is used to calculate particle's position at 2D fracture plane to 3D simulation domain */
{
    double cord3[3];
};


void   Convertto2d()
/*! The function uses rotation matrix and fracture's normal vector to rotate fracture from its position in 3D to XY plane */
{
    printf(" \n Converting 3d nodes coordinates to 2d xy parallel plane \n");
    double check = 0;
    double norm = 0;
    unsigned int i, j, l;
    double nve[3] = {0, 0, 0};
    float angle, anglecos, anglesin;
    
    // loop over all fractures in DFN mesh, defining rotational matrices 3D-2D
    for (j = 0; j < nfract; j++) {
        angle = fracture[j].theta * pi / 180;
        
        for (l = 0; l < 3; l++) {
            fracture[j].rot2mat[0][l] = 0.0;
            fracture[j].rot2mat[1][l] = 0.0;
            fracture[j].rot2mat[2][l] = 0.0;
            fracture[j].rot3mat[0][l] = 0.0;
            fracture[j].rot3mat[1][l] = 0.0;
            fracture[j].rot3mat[2][l] = 0.0;
        }
        
        if (angle != 0.0) {
            anglecos = cos(angle);
            anglesin = sin(angle);
            /* normal vector times e3*/
            nve[0] = fracture[j].nvect_xy[0];
            nve[1] = fracture[j].nvect_xy[1];
            nve[2] = 0.0;
            norm = sqrt(nve[0] * nve[0] + nve[1] * nve[1] + nve[2] * nve[2]);
            nve[0] = nve[0] / norm;
            nve[1] = nve[1] / norm;
            nve[2] = nve[2] / norm;
            check = 0.0;
            // define a rotational matrix form
            fracture[j].rot2mat[0][0] = nve[0] * nve[0] * (1 - anglecos) + anglecos;
            fracture[j].rot2mat[0][1] = nve[0] * nve[1] * (1 - anglecos) - nve[2] * anglesin;
            fracture[j].rot2mat[0][2] = nve[0] * nve[2] * (1 - anglecos) + nve[1] * anglesin;
            fracture[j].rot2mat[1][0] = nve[0] * nve[1] * (1 - anglecos) + nve[2] * anglesin;
            fracture[j].rot2mat[1][1] = nve[1] * nve[1] * (1 - anglecos) + anglecos;
            fracture[j].rot2mat[1][2] = nve[1] * nve[2] * (1 - anglecos) - nve[0] * anglesin;
            fracture[j].rot2mat[2][0] = nve[0] * nve[2] * (1 - anglecos) - nve[1] * anglesin;
            fracture[j].rot2mat[2][1] = nve[1] * nve[2] * (1 - anglecos) + nve[0] * anglesin;
            fracture[j].rot2mat[2][2] = nve[2] * nve[2] * (1 - anglecos) + anglecos;
        } //end if
    } //loop j
    
    /* loop over all nodes in fracture */
    for (i = 0; i < nnodes; i++) {
        if (fracture[node[i].fracture[0] - 1].theta != 0.0) {
            j = node[i].fracture[0] - 1;
            node[i].coord_xy[0] = fracture[j].rot2mat[0][0] * node[i].coord[0] + fracture[j].rot2mat[0][1] * node[i].coord[1] + fracture[j].rot2mat[0][2] * node[i].coord[2];
            node[i].coord_xy[1] = fracture[j].rot2mat[1][0] * node[i].coord[0] + fracture[j].rot2mat[1][1] * node[i].coord[1] + fracture[j].rot2mat[1][2] * node[i].coord[2];
            node[i].coord_xy[2] = fracture[j].rot2mat[2][0] * node[i].coord[0] + fracture[j].rot2mat[2][1] * node[i].coord[1] + fracture[j].rot2mat[2][2] * node[i].coord[2];
        } else {
            /* if angle =0 and fracture is parallel to xy plane, we use the same x and y coordinates */
            node[i].coord_xy[0] = node[i].coord[0];
            node[i].coord_xy[1] = node[i].coord[1];
            node[i].coord_xy[2] = node[i].coord[2];
        }
        
        /** if node belongs to intersection, belongs to two fractures *****/
        if (node[i].fracture[1] != 0) {
            if (fracture[node[i].fracture[1] - 1].theta != 0.0) {
                j = node[i].fracture[1] - 1;
                node[i].coord_xy[3] = fracture[j].rot2mat[0][0] * node[i].coord[0] + fracture[j].rot2mat[0][1] * node[i].coord[1] + fracture[j].rot2mat[0][2] * node[i].coord[2];
                node[i].coord_xy[4] = fracture[j].rot2mat[1][0] * node[i].coord[0] + fracture[j].rot2mat[1][1] * node[i].coord[1] + fracture[j].rot2mat[1][2] * node[i].coord[2];
                node[i].coord_xy[5] = fracture[j].rot2mat[2][0] * node[i].coord[0] + fracture[j].rot2mat[2][1] * node[i].coord[1] + fracture[j].rot2mat[2][2] * node[i].coord[2];
            } else {
                node[i].coord_xy[3] = node[i].coord[0];
                node[i].coord_xy[4] = node[i].coord[1];
                node[i].coord_xy[5] = node[i].coord[2];
            }
        }
    } //loop i
    
    return;
}

///////////////////////////////////////////////////////////////////////////////
/*** function calculates rotation matrix to convert 2D coordinates into 3D*****/

void   Convertto3d()
/*! The function uses rotation matrix to rotate fracture from its position in XY plane to 3D domain*/
{
    double norm = 0;
    unsigned int  j;
    double nve[3] = {0, 0, 0};
    double angle, anglecos, anglesin;
    
    for (j = 0; j < nfract; j++) {
        angle = fracture[j].theta * pi / 180;
        
        if (angle != 0.0) {
            anglecos = cos(angle);
            anglesin = sin(angle);
            /* normal vector times e3*/
            nve[0] = fracture[j].nvect_z[0];
            nve[1] = fracture[j].nvect_z[1];
            nve[2] = 0.0;
            norm = sqrt(nve[0] * nve[0] + nve[1] * nve[1] + nve[2] * nve[2]);
            nve[0] = nve[0] / norm;
            nve[1] = nve[1] / norm;
            nve[2] = nve[2] / norm;
            /* define a rotational matrix form */
            fracture[j].rot3mat[0][0] = nve[0] * nve[0] * (1 - anglecos) + anglecos;
            fracture[j].rot3mat[0][1] = nve[0] * nve[1] * (1 - anglecos) - nve[2] * anglesin;
            fracture[j].rot3mat[0][2] = nve[0] * nve[2] * (1 - anglecos) + nve[1] * anglesin;
            fracture[j].rot3mat[1][0] = nve[0] * nve[1] * (1 - anglecos) + nve[2] * anglesin;
            fracture[j].rot3mat[1][1] = nve[1] * nve[1] * (1 - anglecos) + anglecos;
            fracture[j].rot3mat[1][2] = nve[1] * nve[2] * (1 - anglecos) - nve[0] * anglesin;
            fracture[j].rot3mat[2][0] = nve[0] * nve[2] * (1 - anglecos) - nve[1] * anglesin;
            fracture[j].rot3mat[2][1] = nve[1] * nve[2] * (1 - anglecos) + nve[0] * anglesin;
            fracture[j].rot3mat[2][2] = nve[2] * nve[2] * (1 - anglecos) + anglecos;
        }
    }
    
    return;
}
///////////////////////////////////////////////////////////////////////////////
void ChangeFracture(int cell_win)
/*! This function recalculates particles coordinations at intersection lines. Particles XY coordinations at one fracture are recalculated to 3D positions and then new XY coordinations of an intersecting fracture are defined. */
{
    int j;
    struct posit3d particle3dposit;
    particle3dposit = CalculatePosition3D(particle3dposit);
    j = cell[cell_win - 1].fracture - 1;
    
    if (fracture[j].theta != 0.0) {
        particle[np].position[0] = fracture[j].rot2mat[0][0] * particle3dposit.cord3[0] + fracture[j].rot2mat[0][1] * particle3dposit.cord3[1] + fracture[j].rot2mat[0][2] * particle3dposit.cord3[2];
        particle[np].position[1] = fracture[j].rot2mat[1][0] * particle3dposit.cord3[0] + fracture[j].rot2mat[1][1] * particle3dposit.cord3[1] + fracture[j].rot2mat[1][2] * particle3dposit.cord3[2];
    } else {
        particle[np].position[0] = particle3dposit.cord3[0];
        particle[np].position[1] = particle3dposit.cord3[1];
    }
    
    particle[np].fracture = cell[cell_win - 1].fracture;
    particle[np].cell = cell_win;
    return;
}
////////////////////////////////////////////////////////////////////////////////


struct posit3d CalculatePosition3D()
/*! Function calculates 3D coordinates of current particle's position at 2D fracture plane*/
{
    int j;
    double  thirdcoord = 0.0;
    struct posit3d particle3dposit;
    j = particle[np].fracture - 1;
    
    if (fracture[j].theta != 0.0) {
        if (node[fracture[j].firstnode - 1].fracture[0] == particle[np].fracture) {
            thirdcoord = node[fracture[j].firstnode - 1].coord_xy[2];
        } else if (node[fracture[j].firstnode - 1].fracture[1] == particle[np].fracture) {
            thirdcoord = node[fracture[j].firstnode - 1].coord_xy[5];
        }
        
        particle3dposit.cord3[0] = fracture[j].rot3mat[0][0] * particle[np].position[0] + fracture[j].rot3mat[0][1] * particle[np].position[1] + fracture[j].rot3mat[0][2] * thirdcoord;
        particle3dposit.cord3[1] = fracture[j].rot3mat[1][0] * particle[np].position[0] + fracture[j].rot3mat[1][1] * particle[np].position[1] + fracture[j].rot3mat[1][2] * thirdcoord;
        particle3dposit.cord3[2] = fracture[j].rot3mat[2][0] * particle[np].position[0] + fracture[j].rot3mat[2][1] * particle[np].position[1] + fracture[j].rot3mat[2][2] * thirdcoord;
    } else {
        particle3dposit.cord3[0] = particle[np].position[0];
        particle3dposit.cord3[1] = particle[np].position[1];
        particle3dposit.cord3[2] = node[fracture[j].firstnode - 1].coord[2];
    }
    
    return particle3dposit;
}

///////////////////////////////////////////////////////////////////////////////

void   Velocity3D()
/*! Recalculates 2D velocities at XY fracture plane to 3D velocties in the simulation domain. This procedure is not used for particle tracking, but can be used for velocity field visualization. */
{
    char filename[125];
    sprintf(filename, "%s/Velocity3D", maindir);
    FILE *w3 = OpenFile (filename, "w");
    printf("\n Output flow field: Darcy velocities on nodes in 3D \n");
    fprintf(w3, " node ID number; X-, Y-, Z- node's location; Vx, Vy, Vz of velocity, control cell volume, fracture number \n");
    double cord3[3] = {0, 0, 0};
    unsigned int i, j, v;
    
    /* loop over all nodes in factrure  */
    for (i = 0; i < nnodes; i++) {
        j = node[i].fracture[0] - 1;
        
        if ((node[i].typeN != 2) && (node[i].typeN != 12)) {
            if (fracture[j].theta != 0) {
                // velocity converter
                cord3[0] = fracture[j].rot3mat[0][0] * node[i].velocity[0][0] + fracture[j].rot3mat[0][1] * node[i].velocity[0][1] + fracture[j].rot3mat[0][2] * 0;
                cord3[1] = fracture[j].rot3mat[1][0] * node[i].velocity[0][0] + fracture[j].rot3mat[1][1] * node[i].velocity[0][1] + fracture[j].rot3mat[1][2] * 0;
                cord3[2] = fracture[j].rot3mat[2][0] * node[i].velocity[0][0] + fracture[j].rot3mat[2][1] * node[i].velocity[0][1] + fracture[j].rot3mat[2][2] * 0;
            } else {
                cord3[0] = node[i].velocity[0][0];
                cord3[1] = node[i].velocity[0][1];
                cord3[2] = 0;
            }
            
            fprintf(w3, " %05d  %5.8e   %5.8e   %5.8e %5.8e   %5.8e   %5.8e  %5.8e  %d\n", i + 1, node[i].coord[0], node[i].coord[1], node[i].coord[2], cord3[0], cord3[1], cord3[2], node[i].pvolume, node[i].fracture[0]);
        } else {
            for (v = 0; v < 2; v++) {
                if (fracture[j].theta != 0) {
                    // velocity converter
                    cord3[0] = fracture[j].rot3mat[0][0] * node[i].velocity[v][0] + fracture[j].rot3mat[0][1] * node[i].velocity[v][1] + fracture[j].rot3mat[0][2] * 0;
                    cord3[1] = fracture[j].rot3mat[1][0] * node[i].velocity[v][0] + fracture[j].rot3mat[1][1] * node[i].velocity[v][1] + fracture[j].rot3mat[1][2] * 0;
                    cord3[2] = fracture[j].rot3mat[2][0] * node[i].velocity[v][0] + fracture[j].rot3mat[2][1] * node[i].velocity[v][1] + fracture[j].rot3mat[2][2] * 0;
                } else {
                    cord3[0] = node[i].velocity[v][0];
                    cord3[1] = node[i].velocity[v][1];
                    cord3[2] = 0;
                }
                
                fprintf(w3, " %05d  %5.8e   %5.8e   %5.8e %5.8e   %5.8e   %5.8e  %5.8e  %d\n", i + 1, node[i].coord[0], node[i].coord[1], node[i].coord[2], cord3[0], cord3[1], cord3[2], node[i].pvolume, node[i].fracture[0] );
            }
        }
        
        if ((node[i].fracture[1] != 0) && ((node[i].typeN == 2) || (node[i].typeN == 12))) {
            j = node[i].fracture[1] - 1;
            
            for (v = 2; v < 4; v++) {
                if (fracture[j].theta != 0) {
                    // velocity converter
                    cord3[0] = fracture[j].rot3mat[0][0] * node[i].velocity[v][0] + fracture[j].rot3mat[0][1] * node[i].velocity[v][1] + fracture[j].rot3mat[0][2] * 0;
                    cord3[1] = fracture[j].rot3mat[1][0] * node[i].velocity[v][0] + fracture[j].rot3mat[1][1] * node[i].velocity[v][1] + fracture[j].rot3mat[1][2] * 0;
                    cord3[2] = fracture[j].rot3mat[2][0] * node[i].velocity[v][0] + fracture[j].rot3mat[2][1] * node[i].velocity[v][1] + fracture[j].rot3mat[2][2] * 0;
                } else {
                    cord3[0] = node[i].velocity[v][0];
                    cord3[1] = node[i].velocity[v][1];
                    cord3[2] = 0;
                }
                
                fprintf(w3, " %05d  %5.8e   %5.8e   %5.8e %5.8e   %5.8e   %5.8e  %5.8e  %d\n", i + 1, node[i].coord[0], node[i].coord[1], node[i].coord[2], cord3[0], cord3[1], cord3[2], node[i].pvolume, node[i].fracture[1] );
            }
        }
    }
    
    fclose(w3);
    return;
}
/////////////////////////////////////////////////////////////////////////////
struct posit3d CalculateVelocity3D()
/*! The function converts particle's 2D velocity vector to 3D velocity vector */
{
    int j = particle[np].fracture - 1;
    struct posit3d particle3dvelocity;
    
    // printf(" fracture %d theat %lf \n", j, fracture[j].theta);
    
    if (fracture[j].theta != 0) {
        particle3dvelocity.cord3[0] = fracture[j].rot3mat[0][0] * particle[np].velocity[0] + fracture[j].rot3mat[0][1] * particle[np].velocity[1] + fracture[j].rot3mat[0][2] * 0;
        particle3dvelocity.cord3[1] = fracture[j].rot3mat[1][0] * particle[np].velocity[0] + fracture[j].rot3mat[1][1] * particle[np].velocity[1] + fracture[j].rot3mat[1][2] * 0;
        particle3dvelocity.cord3[2] = fracture[j].rot3mat[2][0] * particle[np].velocity[0] + fracture[j].rot3mat[2][1] * particle[np].velocity[1] + fracture[j].rot3mat[2][2] * 0;
    } else {
        particle3dvelocity.cord3[0] = particle[np].velocity[0];
        particle3dvelocity.cord3[1] = particle[np].velocity[1];
        particle3dvelocity.cord3[2] = 0;
    }
 
    return particle3dvelocity;
}
///////////////////////////////////////////////////////////////////////////
void Coordinations2D ()
/*! The function outputs 2D coordinations of nodes: every fracture into separate file.
 Those files are used as input to gstat for length correlation of aperture. */
{
    printf(" \n Output 2D coordinates of nodes into files \n");
    unsigned int inode, ifract;
    double mincx[nfract], maxcx[nfract], mincy[nfract], maxcy[nfract];
    
    //first, find min and max of coordinations ofr every fracture
    for (ifract = 0; ifract < nfract; ifract++) {
        mincx[ifract] = 100000;
        maxcx[ifract] = -100000;
        mincy[ifract] = 100000;
        maxcy[ifract] = -100000;
        
        for (inode = 0; inode < nnodes; inode++) {
            if (node[inode].fracture[0] == ifract + 1) {
                if (node[inode].coord_xy[0] < mincx[ifract]) {
                    mincx[ifract] = node[inode].coord_xy[0];
                }
                
                if (node[inode].coord_xy[1] < mincy[ifract]) {
                    mincy[ifract] = node[inode].coord_xy[1];
                }
                
                if (node[inode].coord_xy[0] > maxcx[ifract]) {
                    maxcx[ifract] = node[inode].coord_xy[0];
                }
                
                if (node[inode].coord_xy[1] > maxcy[ifract]) {
                    maxcy[ifract] = node[inode].coord_xy[1];
                }
            } else {
                if (node[inode].fracture[1] == ifract + 1) {
                    if (node[inode].coord_xy[3] < mincx[ifract]) {
                        mincx[ifract] = node[inode].coord_xy[3];
                    }
                    
                    if (node[inode].coord_xy[4] < mincy[ifract]) {
                        mincy[ifract] = node[inode].coord_xy[4];
                    }
                    
                    if (node[inode].coord_xy[3] > maxcx[ifract]) {
                        maxcx[ifract] = node[inode].coord_xy[3];
                    }
                    
                    if (node[inode].coord_xy[4] > maxcy[ifract]) {
                        maxcy[ifract] = node[inode].coord_xy[4];
                    }
                }
            }
        }
    }
    
    char filename[15];
    double lengthx, lengthy;
    FILE *fr;
    mkdir("Coord2D", 0777);
    
    for (ifract = 0; ifract < nfract; ifract++) {
        sprintf(filename, "Coord2D/coord_%d.dat", ifract + 1);
        fr = OpenFile(filename, "w");
        lengthx = fabs(maxcx[ifract] - mincx[ifract]);
        lengthy = fabs(maxcy[ifract] - mincy[ifract]);
        
        for (inode = 0; inode < nnodes; inode++) {
            if (node[inode].fracture[0] == ifract + 1) {
                fprintf(fr, "%d   %5.8e    %5.8e   %5.8e    %5.8e  %5.8e\n", inode + 1, node[inode].coord_xy[0], node[inode].coord_xy[1], (node[inode].coord_xy[0] - mincx[ifract]) / lengthx, (node[inode].coord_xy[1] - mincy[ifract]) / lengthy, node[inode].aperture);
            } else if (node[inode].fracture[1] == ifract + 1) {
                fprintf(fr, "%d   %5.8e    %5.8e   %5.8e    %5.8e   %5.8e\n", inode + 1, node[inode].coord_xy[3], node[inode].coord_xy[4], (node[inode].coord_xy[3] - mincx[ifract]) / lengthx, (node[inode].coord_xy[4] - mincy[ifract]) / lengthy, node[inode].aperture);
            }
        }
        
        fclose(fr);
    }
    
    return;
}
////////////////////////////////////////////////////////////////////////////////////
