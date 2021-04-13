#include <stdio.h>
#include <search.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "FuncDef.h"
#include <unistd.h>

struct lb { /*! lb is used in matrix calculation of linear least square */
    double length_b;
    double angle;
    double norm[2];
};

struct matr { /*! matr is used in matrix calculation of linear least square */
    double matrinvG[2][40];
    double matinv[2][2];
};

struct inpfile { /*! reading file name from input dfnTrans control file */
    char filename[120];
    long int flag;
    double param;
};




void  DarcyVelocity()
/*! Function performs Darcy's velocity reconstruction (main function of Darcy velocities reconstruction procedure)
using linear least square algorithm. Flow solver provides
flow fluxes on each edge of control volume cells. Velocity on each control volume cell center (each node) is reconstructed using flow fluxes.*/
/*! Velocity of interior and interior-interface nodes is reconstructed according
 to Eq.5 (Painter,2011); exterior node' velocity according to  Eq.7 (Painter, 2011)*/
/*! Function makes a loop over all nodes and calls functions for velocity reconstruction depending of type of the node (external, internal, internal-interface, external interface)*/

{
    printf("\n Darcy's velocities reconstruction \n");
    double normxarea11[max_neighb - 1][2];
    unsigned int i, j,  l, k1, k2;
    unsigned long int fracture1 = 0, fracture2 = 0;
    unsigned int fract_j1[max_neighb];
    unsigned int fract_j2[max_neighb];
    double length = 1.0;
    struct lb lbound;
    unsigned short int flag1 = 0, flag2 = 0;
    
    for (i = 0; i < nnodes; i++) {
        for (j = 0; j < 4; j++) {
            node[i].velocity[j][0] = 0.;
            node[i].velocity[j][1] = 0.;
        }
        
        if ((node[i].typeN == 0)  || (node[i].typeN == 310) || (node[i].typeN == 210) || (node[i].typeN == 300) || (node[i].typeN == 200))
            /* velocity reconstruction for interior nodes */
            /* 310 is type of exterior nodes in flow-in zone  - as interior node */
            /* 210 is type of exterior nodes in flow-out zone  - as interior node */
        {
            /* calculating norm to edge times edge's area */
            for (j = 0; j < node[i].numneighb; j++) {
                fract_j1[j] = j;
                
                if (node[i].fracture[0] == node[node[i].indnodes[fract_j1[j]] - 1].fracture[0]) {
                    if (pflotran == 1) {
                        length = sqrt(pow(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[0], 2) + pow(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[1], 2));
                        normxarea11[j][0] = -1.0 * (node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[0]) * (node[i].area[j] / (length));
                        normxarea11[j][1] = -1.0 * (node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[1]) * (node[i].area[j] / (length));
                    }
                    
                    if (fehm == 1) {
                        length = sqrt(pow(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[0], 2) + pow(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[1], 2));
                        normxarea11[j][0] = -1.0 * (node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[0]) * (node[i].area[j]);
                        normxarea11[j][1] = -1.0 * (node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[1]) * (node[i].area[j]);
                    }
                }
                
                if (node[i].fracture[0] == node[node[i].indnodes[fract_j1[j]] - 1].fracture[1]) {
                    if (pflotran == 1) {
                        length = sqrt(pow(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[3], 2) + pow(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[4], 2));
                        normxarea11[j][0] = -1.0 * (node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[3]) * (node[i].area[j] / (length));
                        normxarea11[j][1] = -1.0 * (node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[4]) * (node[i].area[j] / (length));
                    }
                    
                    if (fehm == 1) {
                        length = sqrt(pow(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[3], 2) + pow(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[4], 2));
                        normxarea11[j][0] = -1.0 * (node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[3]) * (node[i].area[j]);
                        normxarea11[j][1] = -1.0 * (node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[4]) * (node[i].area[j]);
                    }
                }
            }
            
            VelocityInteriorNode (normxarea11, i, node[i].numneighb, fract_j1, 0);
        }
        
        /* velocity reconstruction for exterior nodes  with Newman b.c.***********/
        if ((node[i].typeN == 10)) {
            unsigned short int edge01 = 200, edge02 = 200, s = 0, kk;
            
            for (j = 0; j < node[i].numneighb; j++) {
                fract_j1[j] = j;
                /* define boundary edges */
                s = 0;
                
                for (kk = 0; kk < 4; kk++) {
                    if (node[i].cells[j][kk] != 0) {
                        s = s + 1;
                    }
                }
                
                if (s == 1) {
                    if (edge01 == 200) {
                        edge01 = j;
                    } else {
                        edge02 = j;
                    }
                }
            }
            
            /* calculating angle between two boundary edges, norm and length */
            if ((edge01 != 200) && (edge02 != 200)) {
                lbound = DefineBoundaryAngle (i, edge01, edge02, node[i].fracture[0], 0);
            } else {
                printf(" Two boundary edges for node %d not found !  \n", i + 1);
            }
            
            /* calculating norm to edge times edge's area, G */
            for (j = 0; j < node[i].numneighb; j++) {
                if (node[i].fracture[0] == node[node[i].indnodes[j] - 1].fracture[0]) {
                    if (pflotran == 1) {
                        length = sqrt(pow(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[0], 2) + pow(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[1], 2));
                        normxarea11[j][0] = -1.*(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[0]) * (node[i].area[j] / (length));
                        normxarea11[j][1] = -1.*(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[1]) * (node[i].area[j] / (length));
                    }
                    
                    if (fehm == 1) {
                        length = sqrt(pow(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[0], 2) + pow(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[1], 2));
                        normxarea11[j][0] = -1.*(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[0]) * (node[i].area[j]);
                        normxarea11[j][1] = -1.*(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[1]) * (node[i].area[j]);
                    }
                }
                
                if (node[i].fracture[0] == node[node[i].indnodes[j] - 1].fracture[1]) {
                    if (pflotran == 1) {
                        length = sqrt(pow(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[3], 2) + pow(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[4], 2));
                        normxarea11[j][0] = -1.*(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[3]) * (node[i].area[j] / (length));
                        normxarea11[j][1] = -1.*(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[4]) * (node[i].area[j] / (length));
                    }
                    
                    if (fehm == 1) {
                        length = sqrt(pow(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[3], 2) + pow(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[4], 2));
                        normxarea11[j][0] = -1.*(node[i].coord_xy[0] - node[node[i].indnodes[j] - 1].coord_xy[3]) * (node[i].area[j]);
                        normxarea11[j][1] = -1.*(node[i].coord_xy[1] - node[node[i].indnodes[j] - 1].coord_xy[4]) * (node[i].area[j]);
                    }
                }
            }
            
            VelocityExteriorNode (normxarea11, i, node[i].numneighb, fract_j1, lbound, 0 );
        }
        
        /* velocity reconstruction for nodes on intersection: ***********/
        /* divide the polygons on 2 parts for each intersecting fracture******/
        /* then divide each part on two again. ******/
        
        if ((node[i].typeN == 12) || (node[i].typeN == 2) || (node[i].typeN == 302) || (node[i].typeN == 202) || (node[i].typeN == 312) || (node[i].typeN == 212)) {
            /* separating polygons into two: two fractures*/
            fracture1 = node[i].fracture[0];
            fracture2 = node[i].fracture[1];
            fract_j1[0] = 0;
            fract_j2[0] = 0;
            k1 = 0;
            k2 = 0;
            
            for (j = 0; j < node[i].numneighb; j++) {
                l = 0;
                flag1 = 0;
                flag2 = 0;
                
                while (node[i].fracts[j][l] != 0) {
                    if (node[i].fracts[j][l] == fracture1) {
                        if (flag1 == 0) {
                            fract_j1[k1] = j;
                            k1++;
                            flag1 = 1;
                        }
                    }
                    
                    if (node[i].fracts[j][l] == fracture2)
                        if (flag2 == 0) {
                            fract_j2[k2] = j;
                            k2++;
                            flag2 = 1;
                        }
                        
                    l++;
                }  // loop on l
            } //loop j
            
            HalfPolygonVelocity(i, k1, fracture1, 0, fract_j1);
            HalfPolygonVelocity(i, k2, fracture2, 2, fract_j2);
        }
    } //loop i
    
    BoundaryCells();
    printf(" Velocities on nodes are calculated \n" );
    //  int res;
    //  struct inpfile inputfile;
    //  inputfile=Control_File("out_2dflow:",11);
    //  res=strncmp(inputfile.filename,"yes",3);
    //  if (res==0)
    //     OutputVelocities();
    return;
}
///////////////////////////////////////////////////////////////////////////////
void OutputVelocities() {
    /*! This function is called to output velocities on nodes in the order of fractture IDs.
     The output can be used to visualise flow field of 2D reconstructed Darcy velocities in
     3D simulation domain */
    char filename[125];
    sprintf(filename, "%s/plot_vel", maindir);
    FILE *wq = fopen (filename, "w");
    sprintf(filename, "%s/fract_nodes", maindir);
    FILE *wn = fopen (filename, "w");
    int f, sumf = 0, i;
    double speed = 0.;
    fprintf(wn, " %d \n", nfract);
    
    for (f = 1; f < nfract + 1; f++) {
        sumf = 0;
        
        for(i = 0; i < nnodes; i++) {
            if (node[i].fracture[0] == f) {
                speed = node[i].velocity[0][0] * node[i].velocity[0][0] + node[i].velocity[0][1] * node[i].velocity[0][1];
                fprintf(wq, " %5.8e %5.8e %5.8e %5.8e %5.8e %5.8e\n",  node[i].coord_xy[0], node[i].coord_xy[1], node[i].velocity[0][0], node[i].velocity[0][1], node[i].pressure, speed);
                sumf = sumf + 1;
                
                if (node[i].velocity[1][0] != 0.) {
                    speed = node[i].velocity[1][0] * node[i].velocity[1][0] + node[i].velocity[1][1] * node[i].velocity[1][1];
                    fprintf(wq, " %5.8e %5.8e %5.8e %5.8e %5.8e %5.8e\n",  node[i].coord_xy[0], node[i].coord_xy[1], node[i].velocity[1][0], node[i].velocity[1][1], node[i].pressure, speed);
                    sumf = sumf + 1;
                }
            } else {
                if (node[i].fracture[1] == f) {
                    speed = node[i].velocity[2][0] * node[i].velocity[2][0] + node[i].velocity[2][1] * node[i].velocity[2][1];
                    fprintf(wq, " %5.8e %5.8e %5.8e %5.8e %5.8e %5.8e\n",  node[i].coord_xy[3], node[i].coord_xy[4], node[i].velocity[2][0], node[i].velocity[2][1], node[i].pressure, speed);
                    sumf = sumf + 1;
                    
                    if (node[i].velocity[3][0] != 0.) {
                        speed = node[i].velocity[3][0] * node[i].velocity[3][0] + node[i].velocity[3][1] * node[i].velocity[3][1];
                        fprintf(wq, " %5.8e %5.8e %5.8e %5.8e %5.8e %5.8e\n",  node[i].coord_xy[3], node[i].coord_xy[4], node[i].velocity[3][0], node[i].velocity[3][1], node[i].pressure, speed);
                        sumf = sumf + 1;
                    }
                }
            }
        }//loop i
        
        fprintf(wn, "%d \n", sumf);
    }// loop f
    
    fclose(wq);
    fclose(wn);
    return;
}
/////////////////////////////////////////////////////////////////////////////
/*! Function performs matrix dot product (GTG)-1 and returns the result. */
struct matr   MatrixProducts (double normxarea[][2],  int number) {
    struct matr matrices;
    double dp[2][2] = {{0, 0}, {0, 0}};
    unsigned int j, m, n;
    
    for (j = 0; j < number; j++) {
        /* dot product (Gt.G) */
        for (m = 0; m < 2; m++) {
            for (n = 0; n < 2; n++) {
                dp[n][m] = dp[n][m] + normxarea[j][n] * normxarea[j][m];
            }
        }
    }
    
    /* calculating Inverse */
    double determinant =  dp[0][0] * dp[1][1] - dp[0][1] * dp[1][0];
    double eps = 1e-75;
    
    if ((determinant < eps) && (determinant > -eps)) {
        //    printf("Det of matrix is close to zero %15.8e  \n",determinant);
        determinant = eps;
    }
    
    double invdet = 1.0 / determinant;
    matrices.matinv[0][0] =  dp[1][1] * invdet;
    matrices.matinv[1][0] = -dp[1][0] * invdet;
    matrices.matinv[0][1] = -dp[0][1] * invdet;
    matrices.matinv[1][1] =  dp[0][0] * invdet;
    
    /* inverse dot product Gt */
    for (m = 0; m < 2; m++) {
        for (j = 0; j < number; j++) {
            matrices.matrinvG[m][j] = matrices.matinv[m][0] * normxarea[j][0] + matrices.matinv[m][1] * normxarea[j][1];
        }
    }
    
    return matrices;
}
///////////////////////////////////////////////////////////////////////////////
struct lb DefineBoundaryAngle(int i, unsigned int edge_1, unsigned int edge_2, int f1, int coorf) {
    /*! The function defines angle between two edges of a boundary cell and return the result. The angle is used in flow velocity reconstruction on fracture edge.*/
    struct lb lbound;
    double  normu, normv;
    double u[2] = {0, 0}, v[2] = {0, 0};
    
    if (node[node[i].indnodes[edge_1] - 1].fracture[0] == f1) {
        u[0] = node[node[i].indnodes[edge_1] - 1].coord_xy[0] - node[i].coord_xy[coorf];
        u[1] = node[node[i].indnodes[edge_1] - 1].coord_xy[1] - node[i].coord_xy[coorf + 1];
    }
    
    if (node[node[i].indnodes[edge_1] - 1].fracture[1] == f1) {
        u[0] = node[node[i].indnodes[edge_1] - 1].coord_xy[3] - node[i].coord_xy[coorf];
        u[1] = node[node[i].indnodes[edge_1] - 1].coord_xy[4] - node[i].coord_xy[coorf + 1];
    }
    
    if (node[node[i].indnodes[edge_2] - 1].fracture[1] == f1) {
        v[0] = node[node[i].indnodes[edge_2] - 1].coord_xy[3] - node[i].coord_xy[coorf];
        v[1] = node[node[i].indnodes[edge_2] - 1].coord_xy[4] - node[i].coord_xy[coorf + 1];
    }
    
    if (node[node[i].indnodes[edge_2] - 1].fracture[0] == f1) {
        v[0] = node[node[i].indnodes[edge_2] - 1].coord_xy[0] - node[i].coord_xy[coorf];
        v[1] = node[node[i].indnodes[edge_2] - 1].coord_xy[1] - node[i].coord_xy[coorf + 1];
    }
    
    lbound.angle = DefineAngle(u[0], u[1], v[0], v[1]);
    normu = sqrt(u[1] * u[1] + u[0] * u[0]);
    normv = sqrt(v[1] * v[1] + v[0] * v[0]);
    
    if (normu > normv) {
        lbound.norm[0] = -u[1];
        lbound.norm[1] = u[0];
    } else {
        lbound.norm[0] = -v[1];
        lbound.norm[1] = v[0];
    }
    
    lbound.length_b = normu + normv;
    return lbound;
}
/////////////////////////////////////////////////////////////////////////////
/*! Function defines an angle between two edges of voronoy cell */
double DefineAngle(double u1, double u2, double v1, double v2) {
    double angle, normu, normv;
    normu = sqrt(u1 * u1 + u2 * u2);
    normv = sqrt(v1 * v1 + v2 * v2);
    angle = acosf(((u1 * v1 + u2 * v2) / (normu * normv)));
    return angle;
}
/////////////////////////////////////////////////////////////////////////////
/*! The function reconstructs Darcy velocity on interior cell center, at interior node */
void VelocityInteriorNode (double normx_area[][2], int i, int number, unsigned int indj[max_neighb], int vi )

{
    short int m, k, j;
    double qhat[2] = {0, 0};
    struct matr matrices;
    double massbalance = 0;
    matrices.matinv[0][0] = 0.0;
    matrices.matinv[0][1] = 0.0;
    matrices.matinv[1][0] = 0.0;
    matrices.matinv[1][1] = 0.0;
    
    for (k = 0; k < 40; k++) {
        matrices.matrinvG[0][k] = 0.0;
        matrices.matrinvG[1][k] = 0.0;
    }
    
    matrices = MatrixProducts (normx_area, number);
    
    for (m = 0; m < 2; m++) {
        qhat[m] = 0;
        
        for (j = 0; j < number; j++) {
            qhat[m] = qhat[m] + matrices.matrinvG[m][j] * node[i].flux[indj[j]];
            massbalance = massbalance + node[i].flux[indj[j]];
        }
        
        // velocity is Darcy's velocity qhat / density * porosity and converted to required time units
        node[i].velocity[vi][m] = (qhat[m] / (density * porosity)) * timeunit;
    }
    
    return;
}
//////////////////////////////////////////////////////////////////////////////
/*! The function reconstructs Darcy velocity on exterior (boundary) node */
void VelocityExteriorNode (double norm_xarea[][2], int i, int number, unsigned int indj[max_neighb], struct lb lbound, int vi) {
    short int m, k, j;
    double qhat[2] = {0, 0};
    struct matr matrices;
    double Bmatr[2] = {0, 0};
    double q_b[2] = {0, 0}, b1[2] = {0, 0}, inv, bqhat, btw[2] = {0, 0};
    double massbalance = 0;
    matrices.matinv[0][0] = 0.0;
    matrices.matinv[0][1] = 0.0;
    matrices.matinv[1][0] = 0.0;
    matrices.matinv[1][1] = 0.0;
    
    for (k = 0; k < 40; k++) {
        matrices.matrinvG[0][k] = 0.0;
        matrices.matrinvG[1][k] = 0.0;
    }
    
    matrices = MatrixProducts (norm_xarea, number);
    
    for (m = 0; m < 2; m++) {
        qhat[m] = 0;
        
        for (j = 0; j < number; j++) {
            qhat[m] = qhat[m] + matrices.matrinvG[m][j] * node[i].flux[indj[j]];
            massbalance = massbalance + node[i].flux[indj[j]];
        }
        
        Bmatr[m] = lbound.norm[m] * lbound.length_b;
    }
    
    // B*qhat
    bqhat = Bmatr[0] * qhat[0] + Bmatr[1] * qhat[1];
    // (GtG)-1 Bt
    b1[0] = Bmatr[0] * matrices.matinv[0][0] + Bmatr[1] * matrices.matinv[1][0];
    b1[1] = Bmatr[0] * matrices.matinv[0][1] + Bmatr[1] * matrices.matinv[1][1];
    // inv [ Bt dot (GtG)-1 B ]
    inv = 1. / (b1[0] * Bmatr[0] + b1[1] * Bmatr[1]);
    // btw= B*inv
    btw[0] = Bmatr[0] * inv;
    btw[1] = Bmatr[1] * inv;
    // GtG*btw
    b1[0] = matrices.matinv[0][0] * btw[0] + matrices.matinv[0][1] * btw[1];
    b1[1] = matrices.matinv[1][0] * btw[0] + matrices.matinv[1][1] * btw[1];
    q_b[0] = qhat[0] - b1[0] * bqhat;
    q_b[1] = qhat[1] - b1[1] * bqhat;
    
    for (m = 0; m < 2; m++) {
        // velocity is Darcy's velocity qhat / density * porosity and converted to required time units
        node[i].velocity[vi][m] = (q_b[m] / (density * porosity)) * timeunit;
    }
    
    return;
}
//////////////////////////////////////////////////////////////////////////////
/*! The function checks velocities at boundary nodes and fixes pathological cases. */
/*! In the rare event, when two velocity vectors are directed towards each other along the same cell edge, a particle will be stuck there. To avoid this situation, one of velocities is redirected along the edge with node associated with lower pressure value. */
void BoundaryCells () {
    long int i, j, n1, n2, n3,  celln = 0;
    
    for(i = 0; i < ncells; i++) {
        /* define k1 and k2 - two boundary nodes in a boundary cell */
        long int k1 = 0, k2 = 0, v1 = 0, v2 = 0, k3 = 0, v3 = 0, node3 = 0,  vel3 = 0, kk3 = 0, vv3 = 0;
        n1 = cell[i].node_ind[0];
        
        if ((node[n1 - 1].typeN == 10) || (node[n1 - 1].typeN == 12) || (node[n1 - 1].typeN == 310) || (node[n1 - 1].typeN == 312)) {
            k1 = n1;
            v1 = cell[i].veloc_ind[0];
        }
        
        n2 = cell[i].node_ind[1];
        n3 = cell[i].node_ind[2];
        
        if ((node[n2 - 1].typeN == 10) || (node[n2 - 1].typeN == 12) || (node[n2 - 1].typeN == 310) || (node[n2 - 1].typeN == 312)) {
            if (k1 == 0) {
                k1 = n2;
                v1 = cell[i].veloc_ind[1];
                node3 = n1;
                vel3 = cell[i].veloc_ind[0];
            } else {
                k2 = n2;
                v2 = cell[i].veloc_ind[1];
                node3 = n3;
                vel3 = cell[i].veloc_ind[2];
            }
        }
        
        if ((node[n3 - 1].typeN == 10) || (node[n3 - 1].typeN == 12) || (node[n3 - 1].typeN == 310) || (node[n3 - 1].typeN == 312)) {
            if (k1 == 0) {
                k1 = n3;
                v1 = cell[i].veloc_ind[2];
            } else {
                if (k2 == 0) {
                    k2 = n3;
                    v2 = cell[i].veloc_ind[2];
                } else {
                    kk3 = n3;
                    vv3 = cell[i].veloc_ind[2];
                }
                
                if (k1 == n1) {
                    node3 = n2;
                    vel3 = cell[i].veloc_ind[1];
                }
            }
        }
        
        if ((k1 * k2 != 0)) {
            /****** first, reconstruct velocities on boundary corners***************/
            /* first node k1 */
            long  int jk3 = 0, jk2 = 0, jk1 = 0, notcorner = 0, notcorner1 = 0, k;
            
            for (j = 0; j < node[k1 - 1].numneighb; j++) {
                if (((node[k1 - 1].type[j] == 10) || (node[k1 - 1].type[j] == 12) || (node[node[k1 - 1].indnodes[j] - 1].typeN == 310)) && (node[k1 - 1].indnodes[j] != k2)) {
                    for (k = 0; k < 4; k++) {
                        if (node[k1 - 1].fracts[j][k] == cell[i].fracture) {
                            if (node[k1 - 1].cells[j][1] == 0) {
                                k3 = node[k1 - 1].indnodes[j];
                                jk3 = j;
                                celln = node[k1 - 1].cells[j][k];
                            }
                        }
                    }
                }
                
                if (node[k1 - 1].indnodes[j] == k2) {
                    jk2 = j;
                }
            }// loop on j
            
            if ((k3 != 0) &&  (node[k1 - 1].cells[jk2][1] == 0) && (node[k1 - 1].cells[jk3][1] == 0))
                /* consider only boundary cells on corner */
            {
                if (cell[celln - 1].node_ind[0] == k3) {
                    v3 = cell[celln - 1].veloc_ind[0];
                }
                
                if (cell[celln - 1].node_ind[1] == k3) {
                    v3 = cell[celln - 1].veloc_ind[1];
                }
                
                if (cell[celln - 1].node_ind[2] == k3) {
                    v3 = cell[celln - 1].veloc_ind[2];
                }
                
                notcorner1 = CornerVelocity(i, k1, k2, k3, v1, v2, v3);
            }
            
            /* check k2, second node on boundary */
            jk3 = 0;
            jk1 = 0;
            
            for (j = 0; j < node[k2 - 1].numneighb; j++) {
                if (((node[k2 - 1].type[j] == 10) || (node[k2 - 1].type[j] == 12) || (node[node[k2 - 1].indnodes[j] - 1].typeN == 310)) && (node[k2 - 1].indnodes[j] != k1)) {
                    for (k = 0; k < 4; k++) {
                        if (node[k2 - 1].fracts[j][k] == cell[i].fracture) {
                            if (node[k2 - 1].cells[j][1] == 0) {
                                k3 = node[k2 - 1].indnodes[j];
                                jk3 = j;
                                celln = node[k2 - 1].cells[j][0];
                            }
                        }
                    }
                }
                
                if (node[k2 - 1].indnodes[j] == k1) {
                    jk1 = j;
                }
            }// loop on j
            
            if ((k3 != 0) &&  (node[k2 - 1].cells[jk1][1] == 0) && (node[k2 - 1].cells[jk3][1] == 0))
                // consider only boundary cells on corner
            {
                if (cell[celln - 1].node_ind[0] == k3) {
                    v3 = cell[celln - 1].veloc_ind[0];
                }
                
                if (cell[celln - 1].node_ind[1] == k3) {
                    v3 = cell[celln - 1].veloc_ind[1];
                }
                
                if (cell[celln - 1].node_ind[2] == k3) {
                    v3 = cell[celln - 1].veloc_ind[2];
                }
                
                notcorner = CornerVelocity(i, k2, k1, k3, v2, v1, v3);
            }
            
            /**** reconstruct velocities on boundary of fracture, end point of intersection ***/
            /*** when two boundary velocities are antiparallel and pointing to each other,
             one of them being turned onto flow direction ****************************/
            if ((notcorner + notcorner1) > 0) {
                double vk1[2] = {0, 0}, vk2[2] = {0, 0}, vk3[2] = {0, 0}, velx, vely, angleuv;
                double angle, eps = 0.0001, node3x = 0, node3y = 0;
                vk1[0] = node[k1 - 1].velocity[v1][0];
                vk1[1] = node[k1 - 1].velocity[v1][1];
                vk2[0] = node[k2 - 1].velocity[v2][0];
                vk2[1] = node[k2 - 1].velocity[v2][1];
                vk3[0] = node[k3 - 1].velocity[v3][0];
                vk3[1] = node[k3 - 1].velocity[v3][1];
                double angle_1;
                angle_1 = DefineAngle(vk1[0], vk1[1], vk2[0], vk2[1]);
                
                /* check those cells on boundaies but not on intersection */
                if ((vk1[0]*vk2[0] < 0) && (vk1[1]*vk2[1] < 0) && (angle_1 < (pi + eps)) && (angle_1 > (pi - eps)) && ((node[k1 - 1].typeN + node[k2 - 1].typeN) == 20)) {
                    //		  printf("corner1, %d %d %lf %lf\n", node[k2-1].fracture[0], k2, node[k2-1].coord_xy[0], node[k2-1].coord_xy[0]);
                    double minpressure = 1000;
                    int ni = 0;
                    
                    for (ni = 0; ni < node[k1 - 1].numneighb; ni++) {
                        if ((node[node[k1 - 1].indnodes[ni] - 1].pressure < minpressure) && (node[k1 - 1].indnodes[ni] != k2)) {
                            minpressure = node[node[k1 - 1].indnodes[ni] - 1].pressure;
                            node3 = node[k1 - 1].indnodes[ni];
                            node3x = node[node3 - 1].coord_xy[XindexC(node3, i)] - node[k1 - 1].coord_xy[0];
                            node3y = node[node3 - 1].coord_xy[YindexC(node3, i)] - node[k1 - 1].coord_xy[1];
                        }
                    }
                    
                    angleuv = DefineAngle(vk1[0], vk1[1], node3x, node3y);
                    velx = vk1[0] * cos(angleuv) - vk1[1] * sin(angleuv);
                    vely = vk1[0] * sin(angleuv) + vk1[1] * cos(angleuv);
                    angle = DefineAngle(velx, vely, node3x, node3y);
                    
                    if (angle > eps) {
                        velx = vk1[0] * cos(angleuv) + vk1[1] * sin(angleuv);
                        vely = -1 * vk1[0] * sin(angleuv) + vk1[1] * cos(angleuv);
                        angle = DefineAngle(velx, vely, node3x, node3y);
                    }
                    
                    if (angle < eps) {
                        node[k1 - 1].velocity[v1][0] = velx;
                        node[k1 - 1].velocity[v1][1] = vely;
                    }
                }
                
                /* check those cells on boundaries and on intersection */
                if ((vk1[0]*vk2[0] < 0) && (vk1[1]*vk2[1] < 0) && ((node[k1 - 1].typeN + node[k2 - 1].typeN) != 20)) {
                    //		 printf("corner2, %d %d %lf %lf\n", node[k2-1].fracture[0], k2, node[k2-1].coord_xy[0], node[k2-1].coord_xy[0]);
                    if (node[k1 - 1].typeN == 12) {
                        node[k1 - 1].velocity[v1][0] = (-1) * node[k1 - 1].velocity[v1][0];
                        node[k1 - 1].velocity[v1][1] = (-1) * node[k1 - 1].velocity[v1][1];
                    } else {
                        if (node[k2 - 1].typeN == 12) {
                            node[k2 - 1].velocity[v2][0] = (-1) * node[k2 - 1].velocity[v2][0];
                            node[k2 - 1].velocity[v2][1] = (-1) * node[k2 - 1].velocity[v2][1];
                        }
                    }
                }
            }
        } //if k1*k2
        
        if((k1 * k2 != 0) && (kk3 != 0)) {
            if (node[kk3 - 1].numneighb == 2) {
                int   notc;
                notc = CornerVelocity(i, kk3, k2, k1, vv3, v2, v1);
            }
        }
    }// loop on i
    
    return;
}

///////////////////////////////////////////////////////////////////////////////
/*! The Function identifies pathologycal cases at corner of fracture boundary.
The angle between velocity on corner node and velocities/edges
 on surrounding boundary nodes are calculated. Then, if velocity is pointing outside of fracture,
 turns the velocity direction along the fracture edge. */

int CornerVelocity(int i, int m1, int m2, int m3, int s1, int s2, int s3) {
    double v[2] = {0, 0}, u[2] = {0, 0}, vk1[2] = {0, 0}, vk2[2] = {0, 0}, vk3[2] = {0, 0}, ang_uv, ang_vk1u, ang_vk1v, ang_vk1vk2, ang_vk1vk3;
    int notcorner;
    // calculate the angle between two boundary edges of the cell i
    // m1 - is a central node,
    // u - is an edge (vector) between nodes m1 and m2
    // v - is an edge between nodes m1 and m3
    // vk1 - velocity of node m1 on cell i
    // vk2 - velocity on node m2 on cell i
    // vk3 - velocity on node m3 on cell i
    // if angle is 0 or pi between velocity of central node and one of the edges and it's velocity, then velocity of central node is rotated on angle with the second edge
    u[0] = node[m2 - 1].coord_xy[XindexC(m2, i)] - node[m1 - 1].coord_xy[XindexC(m1, i)];
    u[1] = node[m2 - 1].coord_xy[YindexC(m2, i)] - node[m1 - 1].coord_xy[YindexC(m1, i)];
    v[0] = node[m3 - 1].coord_xy[XindexC(m3, i)] - node[m1 - 1].coord_xy[XindexC(m1, i)];
    v[1] = node[m3 - 1].coord_xy[YindexC(m3, i)] - node[m1 - 1].coord_xy[YindexC(m1, i)];
    ang_uv = DefineAngle(u[0], u[1], v[0], v[1]);
    /* if current cell is a corner cell then calculate angles of velocities and edges */
    double eps = 0.001,  angle;
    double velx, vely;
    
    if (((ang_uv >= (pi - eps)) && (ang_uv <= (pi + eps))) || ((ang_uv >= (-eps)) && (ang_uv <= (+eps)))) {
        notcorner = 1;
    }
    
    if ((ang_uv < (pi - eps)) && (ang_uv > eps)) {
        notcorner = 0;
        vk1[0] = node[m1 - 1].velocity[s1][0];
        vk1[1] = node[m1 - 1].velocity[s1][1];
        vk2[0] = node[m2 - 1].velocity[s2][0];
        vk2[1] = node[m2 - 1].velocity[s2][1];
        vk3[0] = node[m3 - 1].velocity[s3][0];
        vk3[1] = node[m3 - 1].velocity[s3][1];
        ang_vk1v = DefineAngle(vk1[0], vk1[1], v[0], v[1]);
        ang_vk1u = DefineAngle(vk1[0], vk1[1], u[0], u[1]);
        ang_vk1vk2 = DefineAngle(vk1[0], vk1[1], vk2[0], vk2[1]);
        ang_vk1vk3 = DefineAngle(vk1[0], vk1[1], vk3[0], vk3[1]);
        
        if ((ang_vk1u > (pi - eps)) && (ang_vk1u < (pi + eps)) && ((ang_vk1vk2 < eps) || (ang_vk1vk2 > (pi - eps)))) {
            if ((node[m1 - 1].typeN < 300) && (node[m3 - 1].typeN < 300)) {
                velx = node[m1 - 1].velocity[s1][0] * cos(ang_vk1v) - node[m1 - 1].velocity[s1][1] * sin(ang_vk1v);
                vely = node[m1 - 1].velocity[s1][0] * sin(ang_vk1v) + node[m1 - 1].velocity[s1][1] * cos(ang_vk1v);
                angle = DefineAngle(velx, vely, v[0], v[1]);
                
                if (angle > eps) {
                    velx = node[m1 - 1].velocity[s1][0] * cos(ang_vk1v) + node[m1 - 1].velocity[s1][1] * sin(ang_vk1v);
                    vely = -1 * node[m1 - 1].velocity[s1][0] * sin(ang_vk1v) + node[m1 - 1].velocity[s1][1] * cos(ang_vk1v);
                    angle = DefineAngle(velx, vely, v[0], v[1]);
                }
                
                if (angle < eps) {
                    node[m1 - 1].velocity[s1][0] = velx;
                    node[m1 - 1].velocity[s1][1] = vely;
                }
            }
        } else {
            if ((ang_vk1v > (pi - eps)) && (ang_vk1v < (pi + eps)) && ((ang_vk1vk3 < eps) || (ang_vk1vk3 > (pi - eps)))) {
                if ((node[m1 - 1].typeN < 300) && (node[m2 - 1].typeN < 300)) {
                    velx = node[m1 - 1].velocity[s1][0] * cos(ang_vk1u) - node[m1 - 1].velocity[s1][1] * sin(ang_vk1u);
                    vely = node[m1 - 1].velocity[s1][0] * sin(ang_vk1u) + node[m1 - 1].velocity[s1][1] * cos(ang_vk1u);
                    angle = DefineAngle(velx, vely, u[0], u[1]);
                    
                    if (angle > eps) {
                        velx = node[m1 - 1].velocity[s1][0] * cos(ang_vk1u) + node[m1 - 1].velocity[s1][1] * sin(ang_vk1u);
                        vely = -1 * node[m1 - 1].velocity[s1][0] * sin(ang_vk1u) + node[m1 - 1].velocity[s1][1] * cos(ang_vk1u);
                        angle = DefineAngle(velx, vely, u[0], u[1]);
                    }
                    
                    if (angle < eps) {
                        node[m1 - 1].velocity[s1][0] = velx;
                        node[m1 - 1].velocity[s1][1] = vely;
                    }
                }
            }
        }
        
        /* if node is on inflow boundary:*/
        double ang_u, ang_v;
        
        if (((node[m1 - 1].typeN == 310) || (node[m1 - 1].typeN == 312)) && (node[m2 - 1].typeN != 310) && (node[m2 - 1].typeN != 312)) {
            ang_u = DefineAngle(vk1[0], vk1[1], u[0], u[1]);
            velx = node[m1 - 1].velocity[s1][0] * cos(ang_u) - node[m1 - 1].velocity[s1][1] * sin(ang_u);
            vely = node[m1 - 1].velocity[s1][0] * sin(ang_u) + node[m1 - 1].velocity[s1][1] * cos(ang_u);
            angle = DefineAngle(velx, vely, u[0], u[1]);
            
            if (angle > eps) {
                velx = node[m1 - 1].velocity[s1][0] * cos(ang_u) + node[m1 - 1].velocity[s1][1] * sin(ang_u);
                vely = -1 * node[m1 - 1].velocity[s1][0] * sin(ang_u) + node[m1 - 1].velocity[s1][1] * cos(ang_u);
                angle = DefineAngle(velx, vely, u[0], u[1]);
            }
            
            if (angle < eps) {
                node[m1 - 1].velocity[s1][0] = velx;
                node[m1 - 1].velocity[s1][1] = vely;
            }
        } else {
            if (((node[m1 - 1].typeN == 310) || (node[m1 - 1].typeN == 312)) && (node[m3 - 1].typeN != 310) && (node[m3 - 1].typeN != 312)) {
                ang_v = DefineAngle(vk1[0], vk1[1], v[0], v[1]);
                velx = node[m1 - 1].velocity[s1][0] * cos(ang_v) - node[m1 - 1].velocity[s1][1] * sin(ang_v);
                vely = node[m1 - 1].velocity[s1][0] * sin(ang_v) + node[m1 - 1].velocity[s1][1] * cos(ang_v);
                angle = DefineAngle(velx, vely, v[0], v[1]);
                
                if (angle > eps) {
                    velx = node[m1 - 1].velocity[s1][0] * cos(ang_v) + node[m1 - 1].velocity[s1][1] * sin(ang_v);
                    vely = -1 * node[m1 - 1].velocity[s1][0] * sin(ang_v) + node[m1 - 1].velocity[s1][1] * cos(ang_v);
                    angle = DefineAngle(velx, vely, v[0], v[1]);
                }
                
                if (angle < eps) {
                    node[m1 - 1].velocity[s1][0] = velx;
                    node[m1 - 1].velocity[s1][1] = vely;
                }
            }
        }
    }
    
    return notcorner;
}
/////////////////////////////////////////////////////////////////////////////
int XindexC(int nodenum, int ii) {
    /*! Functions returns the index of X coordination of intersection node (cells)*/
    int xind = 0;
    
    if (node[nodenum - 1].fracture[0] == cell[ii].fracture) {
        xind = 0;
    }
    
    if (node[nodenum - 1].fracture[1] == cell[ii].fracture) {
        xind = 3;
    }
    
    return xind;
}
//////////////////////////////////////////////////////////////////////////////
int YindexC(int nodenum, int ii) {
    /*! Functions returns the index of Y coordination of intersection node (cells)*/
    int yind = 0;
    
    if (node[nodenum - 1].fracture[0] == cell[ii].fracture) {
        yind = 1;
    }
    
    if (node[nodenum - 1].fracture[1] == cell[ii].fracture) {
        yind = 4;
    }
    
    return yind;
}
///////////////////////////////////////////////////////////////////////////////
void HalfPolygonVelocity(int i, int k, int fractn, int indc, unsigned int fractj[max_neighb]) {
    /*! Velocity reconstruction on an intersection node. In this case, the control volume cell is devided onto two polygons by intersection line. The velocity reconstruction is performed on each part of control volume cell at intersection. */
    unsigned int subcell1f[max_neighb], subcell2f[max_neighb];
    unsigned short int sc1f = 0, sc2f = 0, j;
    double inters_v[2] = {0.0, 0.0}, pr, bx = 0, by = 0;
    unsigned  short int s1 = 0, ss = 0, kk, edge11 = 200, edge12 = 200;
    double normxarea21[max_neighb - 1][2];
    double normxarea22[max_neighb - 1][2];
    double length = 1.0;
    struct lb lbound;
    int ic = 0;
    
    if (indc == 2) {
        ic = 3;
    }
    
    for (j = 0; j < k; j++) {
        /* first, check if it is a boundary polygon */
        ss = 0;
        
        for (kk = 0; kk < 4; kk++) {
            if (node[i].cells[fractj[j]][kk] != 0) {
                if (node[i].fracts[fractj[j]][kk] == fractn) {
                    ss = ss + 1;
                }
            }
        }
        
        /* if this edge belongs to one cell in a fracture,
         then it is a boundary edge and boundary angle will be defined */
        if (ss == 1) {
            if (edge11 == 200) {
                edge11 = fractj[j];
            } else {
                edge12 = fractj[j];
            }
            
            s1 = s1 + 1;
        }
        
        /* define a vector of  intersection edge (use it in vector cross product) */
        if ((node[i].type[fractj[j]] == 2) || (node[i].type[fractj[j]] == 12)) {
            inters_v[0] = node[i].coord_xy[ic] - node[node[i].indnodes[fractj[j]] - 1].coord_xy[ic];
            inters_v[1] = node[i].coord_xy[ic + 1] - node[node[i].indnodes[fractj[j]] - 1].coord_xy[ic + 1];
        }
    } //loop j
    
    for (j = 0; j < k; j++) {
        if (node[node[i].indnodes[fractj[j]] - 1].fracture[0] == fractn) {
            bx = node[i].coord_xy[ic] - node[node[i].indnodes[fractj[j]] - 1].coord_xy[0];
            by = node[i].coord_xy[ic + 1] - node[node[i].indnodes[fractj[j]] - 1].coord_xy[1];
            length = sqrt(bx * bx + by * by);
        }
        
        if (node[node[i].indnodes[fractj[j]] - 1].fracture[1] == fractn) {
            bx = node[i].coord_xy[ic] - node[node[i].indnodes[fractj[j]] - 1].coord_xy[3];
            by = node[i].coord_xy[ic + 1] - node[node[i].indnodes[fractj[j]] - 1].coord_xy[4];
            length = sqrt(bx * bx + by * by);
        }
        
        pr = bx * inters_v[1] - by * inters_v[0];
        
        /* sign of product defines the side of edges and devides polygon into
         two subcells: opposite sides from intersection line */
        if (pr <= 0.0) {
            sc1f++;
            subcell1f[sc1f - 1] = fractj[j];
            
            if (fehm == 1) {
                normxarea21[sc1f - 1][0] = -1.*(bx * node[i].area[fractj[j]]);
                normxarea21[sc1f - 1][1] = -1.*(by * node[i].area[fractj[j]]);
            }
            
            if (pflotran == 1) {
                normxarea21[sc1f - 1][0] = -1.*(bx * node[i].area[fractj[j]] / (length));
                normxarea21[sc1f - 1][1] = -1.*(by * node[i].area[fractj[j]] / (length));
            }
            
            if ((node[i].type[fractj[j]] != 2) && (node[i].type[fractj[j]] != 12)) {
                kk = 0;
                
                /* defines indices of velocity vectors */
                do {
                    if (cell[node[i].cells[fractj[j]][kk] - 1].node_ind[0] == i + 1) {
                        cell[node[i].cells[fractj[j]][kk] - 1].veloc_ind[0] = indc;
                    } else if (cell[node[i].cells[fractj[j]][kk] - 1].node_ind[1] == i + 1) {
                        cell[node[i].cells[fractj[j]][kk] - 1].veloc_ind[1] = indc;
                    } else {
                        cell[node[i].cells[fractj[j]][kk] - 1].veloc_ind[2] = indc;
                    }
                    
                    kk++;
                } while (node[i].cells[fractj[j]][kk] != 0);
            }
        }
        
        if (pr >= 0.0) {
            sc2f++;
            subcell2f[sc2f - 1] = fractj[j];
            
            if (fehm == 1) {
                normxarea22[sc2f - 1][0] = -1.*(bx * node[i].area[fractj[j]]);
                normxarea22[sc2f - 1][1] = -1.*(by * node[i].area[fractj[j]]);
            }
            
            if (pflotran == 1) {
                normxarea22[sc2f - 1][0] = -1.*(bx * node[i].area[fractj[j]] / (length));
                normxarea22[sc2f - 1][1] = -1.*(by * node[i].area[fractj[j]] / (length));
            }
            
            if ((node[i].type[fractj[j]] != 2) && (node[i].type[fractj[j]] != 12)) {
                kk = 0;
                
                /* defines indices of velocity vectors */
                do {
                    if (cell[node[i].cells[fractj[j]][kk] - 1].node_ind[0] == i + 1) {
                        cell[node[i].cells[fractj[j]][kk] - 1].veloc_ind[0] = indc + 1;
                    } else if (cell[node[i].cells[fractj[j]][kk] - 1].node_ind[1] == i + 1) {
                        cell[node[i].cells[fractj[j]][kk] - 1].veloc_ind[1] = indc + 1;
                    } else {
                        cell[node[i].cells[fractj[j]][kk] - 1].veloc_ind[2] = indc + 1;
                    }
                    
                    kk++;
                } while (node[i].cells[fractj[j]][kk] != 0);
            }
        }
    }
    
    if ((s1 == 0) || (node[i].typeN == 302) || (node[i].typeN == 202) || (node[i].typeN == 312) || (node[i].typeN == 212)) {
        if (sc1f != 0) {
            VelocityInteriorNode (normxarea21,  i, sc1f, subcell1f, indc);
        }
        
        if (sc2f != 0) {
            VelocityInteriorNode (normxarea22,  i, sc2f, subcell2f, indc + 1);
        }
    } else {
        if (s1 == 2) {
            lbound = DefineBoundaryAngle (i, edge11, edge12, fractn, ic);
            
            if (sc1f != 0) {
                VelocityExteriorNode (normxarea21, i, sc1f, subcell1f, lbound, indc );
            }
            
            if (sc2f != 0) {
                VelocityExteriorNode (normxarea22, i, sc2f, subcell2f, lbound, indc + 1 );
            }
        }
    }
    
    return;
}
///////////////////////////////////////////////////////////////////////////////
