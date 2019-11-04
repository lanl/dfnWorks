#include <stdio.h>
#include <search.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "FuncDef.h"
#include <unistd.h>
#include <time.h>

struct inpfile {
    char filename[120];
    long int flag;
    double param;
};

struct posit3d {
    double cord3[3];
};


int InitPos()
/*! Function defines the required option of particles initial positions defined at input control file; calculates number of particles, allocates memory. */
{
    int i, k_current, k_new = 0, numbf = 1,  frc, firstn, lastn, flag_in = 0, parts_fracture;
    struct inpfile initfile;
    double parts_dist = 0;
    int  zonenumb_in = 0, first_ind = 0, last_ind = 0;
    double ixmin = 0, ixmax = 0, iymin = 0, iymax = 0, izmin = 0, izmax = 0;
    double px[4] = {0.0, 0.0, 0.0, 0.0}, py[4] = {0.0, 0.0, 0.0, 0.0};
    double weight_p = 0.0;
    
    /* calculating number of fractures in in-flow boundary face of the domain ****/
    
    for (i = 0; i < nzone_in; i++) {
        if ((i > 0) && (node[nodezonein[i] - 1].fracture[0] != node[nodezonein[i - 1] - 1].fracture[0])) {
            if  (node[nodezonein[i] - 1].fracture[1] != node[nodezonein[i - 1] - 1].fracture[0])
                //  	printf("fract %d ", node[nodezonein[i]-1].fracture[0]);
            {
                numbf++;
            }
        }
    }
    
    if ((numbf == 0) && (nzone_in != 0)) {
        numbf = 1;
    }
    
    printf(" %d fracture(s) in in-flow boundary zone \n", numbf);
    // define first and last node and their ID for each boundary fracture edge
    unsigned int firstind[numbf], lastind[numbf], firstnode[numbf], lastnode[numbf], numberf = 1, curfr = 0;
    firstnode[0] = nodezonein[0];
    lastnode[0] = nodezonein[0];
    firstind[0] = 0;
    lastind[0] = 0;
    curfr = node[nodezonein[0] - 1].fracture[0];
    
    for (i = 1; i < nzone_in; i++) {
        if ((node[nodezonein[i] - 1].fracture[0] != curfr) && (node[nodezonein[i] - 1].fracture[1] != curfr)) {
            lastnode[numberf - 1] = nodezonein[i - 1];
            lastind[numberf - 1] = i - 1;
            
            if (i < nzone_in - 1) {
                numberf++;
                firstnode[numberf - 1] = nodezonein[i];
                firstind[numberf - 1] = i;
                curfr = node[nodezonein[i] - 1].fracture[0];
            }
        }
    }
    
    lastnode[numberf - 1] = nodezonein[nzone_in - 1];
    lastind[numberf - 1] = nzone_in - 1;
    
    if (numberf > numbf) {
        printf("check the boundary zone file\n");
    }
    
    //  check the input options of particles positions
    double inter_p[numbf][4];
    int inter_fr[numbf];
    int res;
    initfile = Control_File("init_nf:", 8);
    res = strncmp(initfile.filename, "yes", 3);
    
    /*! First option init_nf: equal  number of particles on every boundary edge regardless of edge length*/
    if (res == 0) {
        flag_in = 1;
        flag_w = 1;
        initfile = Control_Data("init_partn:", 11 );
        parts_fracture = initfile.flag;
        printf("\n  %d  particles per boundary fracture edge \n", parts_fracture);
        npart = (numbf + 1) * parts_fracture;
        /*  memory allocatation for particle  */
        particle = (struct contam*) malloc (npart * sizeof(struct contam));
    } else {
        initfile = Control_File("init_eqd:", 9);
        res = strncmp(initfile.filename, "yes", 3);
        
        if (res == 0) {
            flag_in = 2;
            flag_w = 1;
            /*! Second option init_eqd: calculate total length of boundary edges;
            define the distance between particles and place particles
             equidistant from each other on all edges */
            initfile = Control_Data("init_npart:", 11 );
            parts_fracture = initfile.flag;
            npart = (numbf) * parts_fracture * 2;
            /*  memory allocatation for particle structures */
            particle = (struct contam*) malloc ((npart) * sizeof(struct contam));
            // define a distance between particles
            double length2 = 0.0, t_length = 0.0;
            
            for (i = 0; i < numbf; i++) {
                length2 = pow((node[firstnode[i] - 1].coord[0] - node[lastnode[i] - 1].coord[0]), 2) + pow((node[firstnode[i] - 1].coord[1] - node[lastnode[i] - 1].coord[1]), 2) + pow((node[firstnode[i] - 1].coord[2] - node[lastnode[i] - 1].coord[2]), 2);
                t_length = t_length + sqrt(length2);
            }
            
            parts_dist = t_length / (parts_fracture * numbf);
            printf("\n  Particles placed on %f [m]  from each other. Total length %lf  \n", parts_dist, t_length);
        } else {
            initfile = Control_File("init_oneregion:", 15);
            res = strncmp(initfile.filename, "yes", 3);
            
            if (res == 0) {
                flag_in = 3;
                flag_w = 1;
                /*! Third option init_oneregion: user specifies a region and all particles start
                 from the fracture edges that located inside the region */
                initfile = Control_Data("in_partn:", 9 );
                npart = initfile.flag;
                /*  memory allocatation for particle structures */
                particle = (struct contam*) malloc ((npart * 2) * sizeof(struct contam));
                printf("\n Initially particles have the same starting region \n");
                initfile = Control_Param("in_xmin:", 8 );
                ixmin = initfile.param;
                initfile = Control_Param("in_xmax:", 8 );
                ixmax = initfile.param;
                initfile = Control_Param("in_ymin:", 8 );
                iymin = initfile.param;
                initfile = Control_Param("in_ymax:", 8 );
                iymax = initfile.param;
                initfile = Control_Param("in_zmin:", 8 );
                izmin = initfile.param;
                initfile = Control_Param("in_zmax:", 8 );
                izmax = initfile.param;
                initfile = Control_Data("in-flow-boundary:", 17 );
                zonenumb_in = initfile.flag;
                
                /* define coordinations of region according to in-flow zone */
                if ((zonenumb_in == 1) || (zonenumb_in == 2)) {
                    px[0] = ixmin;
                    py[0] = iymin;
                    px[1] = ixmin;
                    py[1] = iymax;
                    px[2] = ixmax;
                    py[2] = iymax;
                    px[3] = ixmax;
                    py[3] = iymin;
                }
                
                if ((zonenumb_in == 3) || (zonenumb_in == 5)) {
                    px[0] = izmin;
                    py[0] = iymin;
                    px[1] = izmin;
                    py[1] = iymax;
                    px[2] = izmax;
                    py[2] = iymax;
                    px[3] = izmax;
                    py[3] = iymin;
                }
                
                if ((zonenumb_in == 4) || (zonenumb_in == 6)) {
                    px[0] = ixmin;
                    py[0] = izmin;
                    px[1] = ixmin;
                    py[1] = izmax;
                    px[2] = ixmax;
                    py[2] = izmax;
                    px[3] = ixmax;
                    py[3] = izmin;
                }
            } else {
                /*! Fourth option init_random: particles will be set randomly over all fractures surfaces; in this case the particles are weighted acoording to the aperture */
                initfile = Control_File("init_random:", 12);
                res = strncmp(initfile.filename, "yes", 3);
                
                if (res == 0) {
                    flag_in = 4;
                    initfile = Control_Data("in_randpart:", 12 );
                    npart = initfile.flag;
                    /*  memory allocatation for particle structures */
                    particle = (struct contam*) malloc ((npart + 1) * sizeof(struct contam));
                    printf("\n Initially particles will be distributed randomly over all fracture surfaces \n");
                    double random_number = 0, sum_aperture = 0.0;
                    unsigned int currentcell, k_curr = 0;
                    
                    do {
                        random_number = drand48();
                        currentcell = random_number * ncells;
                        
                        if ((currentcell != 0) && (((node[cell[currentcell - 1].node_ind[0] - 1].typeN < 200) || (node[cell[currentcell - 1].node_ind[0] - 1].typeN > 250)) && ((node[cell[currentcell - 1].node_ind[1] - 1].typeN < 200) || (node[cell[currentcell - 1].node_ind[1] - 1].typeN > 250)) && ((node[cell[currentcell - 1].node_ind[2] - 1].typeN < 200) || (node[cell[currentcell - 1].node_ind[2] - 1].typeN > 250)))) {
                            particle[k_curr].velocity[0] = 0.;
                            particle[k_curr].velocity[1] = 0.;
                            particle[k_curr].fracture = cell[currentcell - 1].fracture;
                            particle[k_curr].cell = currentcell;
                            particle[k_curr].time = 0.0;
                            Moving2Center (k_curr, currentcell);
                            int insc;
                            insc = InsideCell (currentcell);
                            sum_aperture = sum_aperture + node[cell[currentcell - 1].node_ind[0] - 1].aperture;
                            k_curr++;
                        }
                    } while(k_curr != npart);
                    
                    k_new = k_curr;
                    
                    for (i = 0; i < npart; i++) {
                        particle[i].fl_weight = node[cell[particle[i].cell - 1].node_ind[0] - 1].aperture / sum_aperture;
                    }
                } //end if flag_in=4
                else {
                    /*! 5th option init_matrix: particles are set randomly in rock matrix, their time from initial positions is calculated, then particles move through fractures to out-flow boundary. This option requires preprocessing; the script RandomPositGener.py will provide necessary input files */
                    initfile = Control_File_Optional("init_matrix:", 12);
                    
                    if (initfile.flag > 0) {
                        res = strncmp(initfile.filename, "yes", 3);
                        
                        if (res == 0) {
                            printf(" Initially particles are placed in rock matrix randomly. ");
                            printf(" The closest cells to initial particles positions ");
                            printf(" will be set as starting point in DFN. ");
                            flag_in = 5;
                            InitInMatrix();
                            k_new = npart;
                        } // end if flag_in=5
                        else {
                            initfile = Control_File("init_fluxw:", 11);
                            res = strncmp(initfile.filename, "yes", 3);
                            
                            if (res == 0) {
                                /*! Sixth option init_flux: place particles according to input fluxes. Each particle has the same flux weight. The number of particles are placed propportionally to inflow flux on each cell and fracture edge. */
                                flag_in = 6;
                                flag_w = 0;
                                initfile = Control_Data("init_totalnumber:", 17 );
                                npart = initfile.flag;
                                
                                if (npart < nzone_in) {
                                    printf("\n  The requested number of particles (%d) is less than number of nodes in in-flow boundary (\%d). The initial number of particles is changed to number of nodes in  in-flow boundary. \n", npart, nzone_in);
                                    npart = nzone_in;
                                }
                                
                                weight_p = (totalFluxIn / (float)npart);
                                printf("\n  Requested number of particles %d with flux weight %5.12e (Total Flux %5.12e) \n", npart, weight_p, totalFluxIn);
                                int npart_alloc = 0;
                                npart_alloc = npart * 3;
                                /*  memory allocatation for particle structures */
                                particle = (struct contam*) malloc (npart_alloc * sizeof(struct contam));
                            }
                        }//end if/else flag_in=6
                    } //end if/else flag_in=5
                } //end if flag_in=4
            }	//end if/else flag_in=3
        } //end if /else flag_in=2
    } //end if/else flag_in=1
    
    /* loop on fractures and initial setting of particles */
    k_current = 0;
    
    if ((flag_in <= 2) || (flag_in == 6)) {
        for (i = 0; i < numberf; i++) {
            if (lastnode[i] != firstnode[i]) {
                if (flag_in == 6) { //initial set according to in flow flux
                    k_new = InitParticles_flux(k_current, firstind[i], lastind[i], weight_p);
                    //                printf ("IPF %d %d %d %d %12.5e %d %d %d\n",i+1, k_current, firstind[i], lastind[i], weight_p, firstnode[i], lastnode[i], node[lastnode[i]-1].fracture[0]);
                    k_current = k_new;
                }
                
                if (flag_in == 2) { //equidistant placing of particles on the entire in-flow boundary
                    k_new = InitParticles_eq (k_current, firstnode[i], lastnode[i], parts_dist, firstind[i], lastind[i]);
                    //                 printf("IPE fract first %d fract last %d number parts %d\n", node[firstn-1].fracture[0], node[lastn-1].fracture[0], k_new);
                }
                
                if (flag_in == 1) { //equidistant placing of particles on each fracture
                    k_new = InitParticles_np (k_current, firstnode[i], lastnode[i], parts_fracture, firstind[i], lastind[i]);
                }
                
                k_current = k_new;
            }
        }// end of loop on fractures
    }
    
    frc = node[nodezonein[0] - 1].fracture[0];
    firstn = nodezonein[0];
    lastn = nodezonein[0];
    double thirdcoor = 0.0;
    int firstcoor = 0, secondcoor = 0, frc_count = 0;
    
    if (node[nodezonein[1] - 1].fracture[0] == frc) {
        if (fabs(node[nodezonein[0] - 1].coord[0]) - fabs(node[nodezonein[1] - 1].coord[0]) < 1e-10) {
            firstcoor = 1;
            secondcoor = 2;
        } else {
            firstcoor = 0;
            
            if (fabs(node[nodezonein[0] - 1].coord[1]) - fabs(node[nodezonein[1] - 1].coord[1]) < 1e-10) {
                secondcoor = 2;
            } else {
                secondcoor = 1;
            }
        }
    }
    
    /*** loop on all nodes in zone: define the boundary nodes for each fracture ****/
    //  k_current=0;
    
    //  fprintf(inp,"%d\n", nzone_in);
    for (i = 0; i < nzone_in - 1; i++) {
        //        printf(" %d %d %d  %d %d %d\n", i,nodezonein[i], node[nodezonein[i]-1].fracture[0], node[nodezonein[i]-1].fracture[1], firstn, lastn);
        if (node[nodezonein[i] - 1].fracture[0] == frc) {
            if (node[nodezonein[i] - 1].coord[firstcoor] != node[firstn - 1].coord[firstcoor]) {
                if (node[nodezonein[i] - 1].coord[firstcoor] < node[firstn - 1].coord[firstcoor]) {
                    firstn = nodezonein[i];
                    first_ind = i;
                }
                
                if (node[nodezonein[i] - 1].coord[firstcoor] > node[lastn - 1].coord[firstcoor]) {
                    lastn = nodezonein[i];
                    last_ind = i;
                }
                
                //	  fprintf(inp,"first coord, %d %d\n",firstn, lastn);
            } else {
                if (node[nodezonein[i] - 1].coord[secondcoor] < node[firstn - 1].coord[secondcoor]) {
                    firstn = nodezonein[i];
                    first_ind = i;
                }
                
                if (node[nodezonein[i] - 1].coord[secondcoor] > node[lastn - 1].coord[secondcoor]) {
                    lastn = nodezonein[i];
                    last_ind = i;
                }
                
                //		fprintf(inp,"second coord, %d %d\n",firstn, lastn);
            }
        }
        
        //  printf("fracture in flow-in zone %d first node %d last node %d \n", frc, firstn, lastn);
        if ((node[nodezonein[i] - 1].fracture[0] != frc) || ((i == nzone_in - 2))) {
            //	   printf("fracture in flow-in zone %d first node %d last node %d \n", frc, firstn, lastn);
            if ((i == nzone_in - 2)  && (node[firstn - 1].fracture[0] == node[nodezonein[nzone_in - 1] - 1].fracture[0])) {
                lastn = nodezonein[nzone_in - 1];
                last_ind = nzone_in - 1;
            }
            
            if (firstn == lastn) {
                //printf("firstn %d lastn %d fracture %d %d \n", firstn, lastn, node[nodezonein[i]-1].fracture[0],node[nodezonein[i]-1].fracture[1] );
            }
            
            if (firstn != lastn) {
                if (flag_in == 3) {
                    double cx1 = 0, cx2 = 0, cy1 = 0, cy2 = 0;
                    /* define ends points of fracture edge, then calculate an intersection with starting region */
                    inter_p[frc_count][0] = 1e-10;
                    inter_p[frc_count][1] = 1e-10;
                    inter_p[frc_count][2] = 1e-10;
                    inter_p[frc_count][3] = 1e-10;
                    
                    if ((zonenumb_in == 1) || (zonenumb_in == 2)) {
                        cx1 = node[firstn - 1].coord[0];
                        cy1 = node[firstn - 1].coord[1];
                        
                        if ((cx1 > ixmin) && (cx1 < ixmax) && (cy1 > iymin) && (cy1 < iymax)) {
                            inter_p[frc_count][0] = cx1;
                            inter_p[frc_count][1] = cy1;
                        }
                        
                        cx2 = node[lastn - 1].coord[0];
                        cy2 = node[lastn - 1].coord[1];
                        
                        if ((cx2 > ixmin) && (cx2 < ixmax) && (cy2 > iymin) && (cy2 < iymax)) {
                            inter_p[frc_count][0] = cx2;
                            inter_p[frc_count][1] = cy2;
                        }
                        
                        thirdcoor = node[firstn - 1].coord[2];
                    }
                    
                    if ((zonenumb_in == 3) || (zonenumb_in == 5)) {
                        cx1 = node[firstn - 1].coord[2];
                        cy1 = node[firstn - 1].coord[1];
                        
                        if ((cx1 > izmin) && (cx1 < izmax) && (cy1 > iymin) && (cy1 < iymax)) {
                            inter_p[frc_count][0] = cx1;
                            inter_p[frc_count][1] = cy1;
                        }
                        
                        cx2 = node[lastn - 1].coord[2];
                        cy2 = node[lastn - 1].coord[1];
                        
                        if ((cx2 > izmin) && (cx2 < izmax) && (cy2 > iymin) && (cy2 < iymax)) {
                            inter_p[frc_count][0] = cx2;
                            inter_p[frc_count][1] = cy2;
                        }
                        
                        thirdcoor = node[firstn - 1].coord[0];
                    }
                    
                    if ((zonenumb_in == 4) || (zonenumb_in == 6)) {
                        cx1 = node[firstn - 1].coord[0];
                        cy1 = node[firstn - 1].coord[2];
                        
                        if ((cx1 > ixmin) && (cx1 < ixmax) && (cy1 > izmin) && (cy1 < izmax)) {
                            inter_p[frc_count][0] = cx1;
                            inter_p[frc_count][1] = cy1;
                        }
                        
                        cx2 = node[lastn - 1].coord[0];
                        cy2 = node[lastn - 1].coord[2];
                        
                        if ((cx2 > ixmin) && (cx2 < ixmax) && (cy2 > izmin) && (cy2 < izmax)) {
                            inter_p[frc_count][0] = cx2;
                            inter_p[frc_count][1] = cy2;
                        }
                        
                        thirdcoor = node[firstn - 1].coord[1];
                    }
                    
                    double pr1, pr2, pr3, pr4, p_x, p_y;
                    int ii;
                    
                    /* define intersection points of boundary fracture edges and starting region sides*/
                    for (ii = 0; ii < 4; ii++) {
                        int kk;
                        kk = ii + 1;
                        
                        if (ii == 3) {
                            kk = 0;
                        }
                        
                        pr1 = (px[ii] - cx1) * (py[kk] - cy1) - (py[ii] - cy1) * (px[kk] - cx1);
                        pr2 = (cx1 - px[ii]) * (cy2 - py[ii]) - (cy1 - py[ii]) * (cx2 - px[ii]);
                        pr3 = (px[ii] - cx2) * (py[kk] - cy2) - (py[ii] - cy2) * (px[kk] - cx2);
                        pr4 = (cx1 - px[kk]) * (cy2 - py[kk]) - (cy1 - py[kk]) * (cx2 - px[kk]);
                        
                        if ((pr1 * pr3 < 0) && (pr2 * pr4 < 0)) {
                            pr1 = cx1 * cy2 - cy1 * cx2;
                            pr2 = px[ii] * py[kk] - py[ii] * px[kk];
                            pr3 = (cx1 - cx2) * (py[ii] - py[kk]) - (cy1 - cy2) * (px[ii] - px[kk]);
                            p_x = ((px[ii] - px[kk]) * pr1 - (cx1 - cx2) * pr2) / pr3;
                            p_y = ((py[ii] - py[kk]) * pr1 - (cy1 - cy2) * pr2) / pr3;
                            
                            if (inter_p[frc_count][0] == 1e-10) {
                                inter_p[frc_count][0] = p_x;
                                inter_p[frc_count][1] = p_y;
                            } else {
                                inter_fr[frc_count] = frc;
                                inter_p[frc_count][2] = p_x;
                                inter_p[frc_count][3] = p_y;
                                frc_count++;
                                break;
                            }
                        }
                    }
                } //end of flag
            }
            
            if (i < nzone_in - 2) {
                frc = node[nodezonein[i] - 1].fracture[0];
                firstn = nodezonein[i];
                first_ind = i;
                lastn = nodezonein[i];
                last_ind = i;
                
                //		  fprintf(inp,"p %d %d %d %d\n", i, frc, firstn, lastn);
                if (node[nodezonein[i + 1] - 1].fracture[0] == frc) {
                    if (abs(node[nodezonein[i] - 1].coord[0]) - abs(node[nodezonein[i + 1] - 1].coord[0]) < 1e-10) {
                        firstcoor = 1;
                        secondcoor = 2;
                    } else {
                        firstcoor = 0;
                        
                        if (abs(node[nodezonein[i] - 1].coord[1]) - abs(node[nodezonein[i + 1] - 1].coord[1]) < 1e-10) {
                            secondcoor = 2;
                        } else {
                            secondcoor = 1;
                        }
                    }
                }
            }
        }
    }
    
    //   printf("fracture in flow-in zone %d first node %d last node %d \n", frc, firstn, lastn);
    if ((flag_in == 3) && (frc_count == 0)) {
        printf("\n There is no fracture crosses the given range. Try to increase the range. \n");
        printf("\n Program is terminated. \n");
        exit(1);
    }
    
    /* place particles in starting region: every fracture (or part of fracture
     edge will have the same amount of particles */
    if (flag_in == 3) {
        for (i = 0; i < frc_count; i++) {
            parts_fracture = (int) npart / frc_count;
            k_new = InitParticles_ones (k_current, inter_p, inter_fr[i], parts_fracture, i, thirdcoor, zonenumb_in, first_ind, last_ind);
            k_current = k_new;
            //   printf(" %d intersects at %f %f %f %f\n",i, inter_p[i][0], inter_p[i][1], inter_p[i][2], inter_p[i][3]);
        }
    }
    
    // fclose(inp);
    if (flag_in == 0) {
        printf("\n There is no option specified for particles initial positions! \n");
        printf("\n Program is terminated. \n");
        exit(1);
    }
    
    return k_new;
}


/////////////////////////////////////////////////////////////////////////////

int InitCell ()
/*! Function performs a search to find cell Id where the particle was initially placed.*/
{
    int i, j, k, curcel, insc = 0;
    
    for (i = 0; i < nzone_in; i++) {
        for (j = 0; j < node[nodezonein[i] - 1].numneighb; j++) {
            for (k = 0; k < 4; k++)
                if (node[nodezonein[i] - 1].cells[j][k] != 0) {
                    curcel = node[nodezonein[i] - 1].cells[j][k];
                    insc = InsideCell (curcel);
                    
                    if (insc == 1) {
                        break;
                    }
                }
                
            if (insc == 1) {
                break;
            }
        }
        
        if (insc == 1) {
            break;
        }
    }
    
    //   if (insc==0)
    //  {
    // printf("Init Cell: NOT FOUND \n");
    //  printf("%d find cell: particle cell %d   \n", np, particle[np].cell);
    //      }
    return insc;
}
////////////////////////////////////////////////////////////////////////////

int InitParticles_np (int k_current, int firstnd, int lastnd, int parts_fracture, int first_ind, int last_ind)
/*! Function defines particle's initial positions on a single fracture edge. Option #1, init_nf */
{
    double deltax, deltay;
    int j, pf;
    pf = parts_fracture;
    int ii, jj,  k, curcel, insc = 0;
    deltax = fabs(node[nodezonein[last_ind]-1].coord_xy[0] - node[nodezonein[first_ind]-1].coord_xy[0]);
    deltay = fabs(node[nodezonein[last_ind]-1].coord_xy[1] - node[nodezonein[first_ind]-1].coord_xy[1]);
   
 //   printf ("%d  %d %d %d %f %f\n", first_ind, last_ind,  firstnd, lastnd, deltax, deltay);
  
    
    for (j = 0; j < pf; j++) {
        if (node[firstnd - 1].coord_xy[0] < node[lastnd - 1].coord_xy[0]) {
            particle[k_current].position[0] = node[firstnd - 1].coord_xy[0] + (deltax / pf) * (j) + deltax / (2.0 * pf);
        } else {
            particle[k_current].position[0] = node[firstnd - 1].coord_xy[0] - (deltax / pf) * (j) - deltax / (2.0 * pf);
        }
        
        if (node[firstnd - 1].coord_xy[1] < node[lastnd - 1].coord_xy[1]) {
            particle[k_current].position[1] = node[firstnd - 1].coord_xy[1] + (deltay / pf) * (j) + deltay / (2.0 * pf);
        } else {
            particle[k_current].position[1] = node[firstnd - 1].coord_xy[1] - (deltay / pf) * (j) - deltay / (2.0 * pf);
        }
        
        particle[k_current].velocity[0] = 0.;
        particle[k_current].velocity[1] = 0.;
        particle[k_current].fracture = node[firstnd - 1].fracture[0];
        particle[k_current].intcell = 0;
        particle[k_current].time = 0.0;
        particle[k_current].fl_weight = 0.0;
        k_current++;
        
        if (k_current > npart) {
            printf(" \n Number of particles with allocated memory is less than number of particles set up initially. \n");
            printf(" Increase the number of particles. Program is terminated. \n");
            exit(1);
        }
    }
    
    return k_current;
}
////////////////////////////////////////////////////////////////////////////

int InitParticles_eq (int k_current, int firstn, int lastn, double parts_dist, int first_ind, int last_ind)
/*! Function defines particles initial positions at a single fracture edge, using calculated before distance between particles. Option #2, init_eqd. */
{
    double deltax, deltay, edgelength, eqdist_x, eqdist_y;
    unsigned int j, pf;
    deltax = (node[lastn - 1].coord_xy[0] - node[firstn - 1].coord_xy[0]);
    deltay = (node[lastn - 1].coord_xy[1] - node[firstn - 1].coord_xy[1]);
    edgelength = sqrt(deltax * deltax + deltay * deltay);
    pf = (int)(edgelength / parts_dist);
    
    if (pf < 2) {
        pf = 1;
        eqdist_x = deltax / 2.0;
        eqdist_y = deltay / 2.0;
    } else {
        eqdist_x = deltax / pf;
        eqdist_y = deltay / pf;
    }
    
    for (j = 0; j < pf; j++) {
        particle[k_current].position[0] = node[firstn - 1].coord_xy[0] + eqdist_x * (j) + eqdist_x / 2.0;
        particle[k_current].position[1] = node[firstn - 1].coord_xy[1] + eqdist_y * (j) + eqdist_y / 2.0;
        particle[k_current].velocity[0] = 0.;
        particle[k_current].velocity[1] = 0.;
        particle[k_current].fracture = node[firstn - 1].fracture[0];
        particle[k_current].intcell = 0;
        particle[k_current].time = 0.0;
        particle[k_current].fl_weight = 0.0;
        
        if (particle[k_current].fracture == 13) {
            printf("os %lf %lf \n", particle[k_current].position[0], particle[k_current].position[1]);
        }
        
        k_current++;
        
        if (k_current > npart) {
            printf("\n Number of particles with allocated memory is less than number of particles set up initially. \n");
            printf(" Increase the number of particles. Program is terminated. \n");
            exit(1);
        }
    }
    
    return k_current;
}
////////////////////////////////////////////////////////////////////////////

int InitParticles_ones (int k_current, double inter_p[][4], int fracture_n, int parts_fracture, int ii, double thirdcoor, int zonenumb_in, int first_ind, int last_ind)
/*! Function defines particles initial positions in option #3, where user defines region at in-flow boundary face for particles. */
{
    int j = fracture_n - 1;
    double x_1 = 0, y_1 = 0, z_1 = 0, x_2 = 0, z_2 = 0, y_2 = 0;
    double x1cor = 0.0, y1cor = 0.0, z1cor = 0, x2cor = 0.0, y2cor = 0.0, z2cor = 0;
    
    if ((zonenumb_in == 1) || (zonenumb_in == 2)) {
        x1cor = inter_p[ii][0];
        y1cor = inter_p[ii][1];
        z1cor = thirdcoor;
        x2cor = inter_p[ii][2];
        y2cor = inter_p[ii][3];
        z2cor = thirdcoor;
    }
    
    if ((zonenumb_in == 3) || (zonenumb_in == 5)) {
        x1cor = thirdcoor;
        x2cor = thirdcoor;
        z1cor = inter_p[ii][0];
        z2cor = inter_p[ii][2];
        y1cor = inter_p[ii][1];
        y2cor = inter_p[ii][3];
    }
    
    if ((zonenumb_in == 4) || (zonenumb_in == 6)) {
        y1cor = thirdcoor;
        y2cor = thirdcoor;
        x1cor = inter_p[ii][0];
        x2cor = inter_p[ii][2];
        z1cor = inter_p[ii][1];
        z2cor = inter_p[ii][3];
    }
    
    if (fracture[j].theta != 0.0) {
        x_1 = fracture[j].rot2mat[0][0] * x1cor + fracture[j].rot2mat[0][1] * y1cor + fracture[j].rot2mat[0][2] * z1cor;
        y_1 = fracture[j].rot2mat[1][0] * x1cor + fracture[j].rot2mat[1][1] * y1cor + fracture[j].rot2mat[1][2] * z1cor;
        z_1 = fracture[j].rot2mat[2][0] * x1cor + fracture[j].rot2mat[2][1] * y1cor + fracture[j].rot2mat[2][2] * z1cor;
        x_2 = fracture[j].rot2mat[0][0] * x2cor + fracture[j].rot2mat[0][1] * y2cor + fracture[j].rot2mat[0][2] * z2cor;
        y_2 = fracture[j].rot2mat[1][0] * x2cor + fracture[j].rot2mat[1][1] * y2cor + fracture[j].rot2mat[1][2] * z2cor;
        z_2 = fracture[j].rot2mat[2][0] * x2cor + fracture[j].rot2mat[2][1] * y2cor + fracture[j].rot2mat[2][2] * z2cor;
    } else {
        /* if angle =0 and fracture is parallel to xy plane, we use the same x and y coordinates */
        x_1 = x1cor;
        y_1 = y1cor;
        z_1 = z1cor;
        x_2 = x2cor;
        y_2 = y2cor;
        z_2 = z2cor;
    }
    
    double deltax, deltay;
    unsigned int  pf;
    pf = parts_fracture;
    deltax = (x_2 - x_1);
    deltay = (y_2 - y_1);
    
    for (j = 0; j < pf; j++) {
        particle[k_current].position[0] = x_1 + (deltax / pf) * (j) + deltax / (2.0 * pf);
        particle[k_current].position[1] = y_1 + (deltay / pf) * (j) + deltay / (2.0 * pf);
        particle[k_current].velocity[0] = 0.;
        particle[k_current].velocity[1] = 0.;
        particle[k_current].fracture = fracture_n;
        particle[k_current].intcell = 0;
        particle[k_current].time = 0.0;
        particle[k_current].fl_weight = 0.0;
        k_current++;
        
        if (k_current > npart) {
            printf(" \n Number of particles with allocated memory is less than number of particles set up initially. \n");
            printf(" Increase the number of particles. Program is terminated. \n");
            exit(1);
        }
    }
    
    return k_current;
}
////////////////////////////////////////////////////////////////////////////
void FlowInWeight(int numberpart)
/*! Function calculates particle's in-flow flux weight. Used in option #1, #2, #3. */
{
    int ind1 = 0, ind2 = 0, ver1 = 0, ver2 = 0, ver3 = 0, incell = 0, n1in = 0, n2in = 0, jj;
    int ins;
    double sumflux1 = 0, sumflux2 = 0, particleflux[numberpart], totalflux = 0;
    
    for (np = 0; np < numberpart; np++) {
        ins = 0;
        ins = InitCell();
        incell = particle[np].cell;
        
        if (incell != 0) {
            incell = particle[np].cell;
            ver1 = cell[incell - 1].node_ind[0];
            ver2 = cell[incell - 1].node_ind[1];
            ver3 = cell[incell - 1].node_ind[2];
            n1in = 0;
            n2in = 0;
            
            if (node[ver1 - 1].typeN >= 300) {
                n1in = ver1;
                ind1 = 0;
            }
            
            if (node[ver2 - 1].typeN >= 300) {
                if (n1in == 0) {
                    n1in = ver2;
                    ind1 = 1;
                } else {
                    n2in = ver2;
                    ind2 = 1;
                }
            }
            
            if (node[ver3 - 1].typeN >= 300) {
                if (n1in == 0) {
                    n1in = ver3;
                    ind1 = 2;
                } else {
                    n2in = ver3;
                    ind2 = 2;
                }
            }
            
            if ((n1in != 0) && (n2in != 0)) {
                sumflux1 = 0;
                sumflux2 = 0;
                
                for (jj = 0; jj < node[n1in - 1].numneighb; jj++) {
                    sumflux1 = sumflux1 + fabs(node[n1in - 1].flux[jj]);
                }
                
                for (jj = 0; jj < node[n2in - 1].numneighb; jj++) {
                    sumflux2 = sumflux2 + fabs(node[n2in - 1].flux[jj]);
                }
                
                particleflux[np] = particle[np].weight[ind1] * sumflux1 + particle[np].weight[ind2] * sumflux2;
                totalflux = totalflux + particleflux[np];
            } else {
                int ncent = 0;
                ncent = n1in + n2in;
                
                if (ncent != 0) {
                    sumflux1 = 0;
                    
                    for (jj = 0; jj < node[ncent - 1].numneighb; jj++) {
                        sumflux1 = sumflux1 + fabs(node[ncent - 1].flux[jj]);
                    }
                    
                    particleflux[np] = sumflux1;
                    totalflux = totalflux + particleflux[np];
                }
            }
        }
    }
    
    for (np = 0; np < numberpart; np++) {
        particle[np].fl_weight = particleflux[np] / totalflux;
        // printf("%d   %5.12e %5.12e  %5.12e  \n", np+1,particleflux[np], totalflux, particle[np].fl_weight);
    }
    
    return;
}
//////////////////////////////////////////////////////////////////////////
void InitInMatrix()
/*! Function performs data reading from files for Option #5, init_matrix. In this option particles are placed at random positions in matrix, the time to move from initial position to nearest fracture is calculated in function TimeFromMatrix.*/
/*! Input files ParticleInitCoordR.dat and ClosestNodeR.inp provide particles initial positions at matrix and te closes node ID at DFN mesh, respectively. */

{
    struct inpfile inputfile;
    inputfile = Control_File("inm_coord:", 10 );
    FILE *mc = OpenFile (inputfile.filename, "r");
    printf("\n OPEN AND READ FILE: %s \n \n", inputfile.filename);
    inputfile = Control_File("inm_nodeID:", 10 );
    FILE *mn = OpenFile (inputfile.filename, "r");
    printf("\n OPEN AND READ FILE: %s \n \n", inputfile.filename);
    //FILE *mdf=OpenFile("distance_time.dat","w");
    int i, ii;
    unsigned int number, no;
    char cs;
    
    if (fscanf(mn, "%d  %d %d %d %d \n", &no, &no, &number, &no, &no) != 5) {
        printf("error");
    }
    
    for (i = 0; i < (number + 1); i++) {
        do {
            cs = fgetc(mn);
        } while (cs != '\n');
    }
    
    if (fscanf(mc, " %d \n", &npart) != 1) {
        printf("error");
    }
    
    /*  memory allocatation for particle structures */
    particle = (struct contam*) malloc ((npart + 1) * sizeof(struct contam));
    double* distance = malloc ((npart + 1) * sizeof(double));
    double xp, yp, zp,  sum_distance = 0.0, xp2, yp2, zp2;
    
    for (ii = 0; ii < npart; ii++) {
        if (fscanf(mn, " %d  %d   %d  %d  %d  %d \n", &no, &no, &no, &no, &no, &number) != 6) {
            printf("error");
        }
        
        if (fscanf(mc, " %lf %lf %lf \n ", &xp, &yp, &zp) != 1) {
            printf ("error");
        }
        
        xp2 = (node[number - 1].coord[0] - xp) * (node[number - 1].coord[0] - xp);
        yp2 = (node[number - 1].coord[1] - yp) * (node[number - 1].coord[1] - yp);
        zp2 = (node[number - 1].coord[2] - zp) * (node[number - 1].coord[2] - zp);
        distance[ii] = sqrt(xp2 + yp2 + zp2);
        particle[ii].velocity[0] = 0.;
        particle[ii].velocity[1] = 0.;
        particle[ii].fracture = node[number - 1].fracture[0];
        particle[ii].cell = 0;
        particle[ii].position[0] = node[number - 1].coord_xy[0];
        particle[ii].position[1] = node[number - 1].coord_xy[1];
        particle[ii].time = 0.0;
        particle[ii].weight[0] = 0.0;
        particle[ii].weight[1] = 0.0;
        particle[ii].weight[2] = 0.0;
        particle[ii].prev_pos[0] = 0.0;
        particle[ii].prev_pos[1] = 0.0;
        particle[ii].intcell = 0;
        particle[ii].fl_weight = 0.0;
        // define a time that took for particle to reach fracture from a rock matrix
        particle[ii].time = TimeFromMatrix(distance[ii]);
        sum_distance = sum_distance + distance[ii];
    }
    
    fclose(mc);
    fclose(mn);
    
    //define weights according to distance from fracture
    for (i = 0; i < npart; i++) {
        particle[i].fl_weight = distance[i] / sum_distance;
    }
    
    free(distance);
    return;
}
///////////////////////////////////////////////////////////////////////////
double TimeFromMatrix(double pdist)
/*! Option #5. Estimation of travel time of particles moving from matrix to the closest fracture. */
{
    struct inpfile inputfile;
    double ptime = 0.0, ptime1 = 0.0, ptime2 = 0.0;
    double randomnumber = 0.0;
    randomnumber = drand48();
    double mporosity = 0.0;
    double mdiffcoeff = 0.0;
    inputfile = Control_Param("inm_porosity:", 13);
    mporosity = inputfile.param;
    inputfile = Control_Param("inm_diffcoeff:", 14);
    mdiffcoeff = inputfile.param;
    //  printf("diff coeff %5.9e porosity %lf \n",mdiffcoeff, mporosity);
    double retardation_factor = 1.0;
    double inverse_erfc = 0.0;
    double z;
    z = 1 - randomnumber;
    inverse_erfc = 0.5 * sqrt(pi) * (z + (pi / 12) * pow(z, 3) + ((7 * pow(pi, 2)) / 480) * pow(z, 5) + ((127 * pow(pi, 3)) / 40320) * pow(z, 7) + ((4369 * pow(pi, 4)) / 5806080) * pow(z, 9) + ((34807 * pow(pi, 5)) / 182476800) * pow(z, 11));
    ptime2 = (1.0 / inverse_erfc) * (1.0 / inverse_erfc);
    ptime1 = (pdist * pdist) / (4.0 * (mporosity * mdiffcoeff / retardation_factor));
    ptime = (ptime1 * ptime2) / timeunit;
    return ptime;
}
////////////////////////////////////////////////////////////////////////

int InitParticles_flux (int k_current, int first_ind, int last_ind, double weight_p)
/*! Function defines particle's initial positions at single fracture edge in Option #6. Particles are placed according to input flux weights. In this case, all the particles have  the same flux weight, but number of particles per fracture edge depends on in-flow flux of this fracture. */

{
    double deltax, deltay, edgelength, eqdist_x, eqdist_y, sumflux = 0, startpos_x, startpos_y, sumdelta = 0.0;
    double sumfluxfract = 0.0;
    unsigned int i, k, j, jj, pf, curcel = 0, insc = 0, np, np_init;
    struct posit3d particle3dposition;
    np_init = k_current;
    
    //  printf("firstn %d lastn %d \n", first_ind, last_ind);
    for (j = first_ind; j <= last_ind; j++) {
        sumflux = 0.0;
        
        // calculate the flux of the current cell
        for (jj = 0; jj < node[nodezonein[j] - 1].numneighb; jj++) {
            sumflux = sumflux + (node[nodezonein[j] - 1].flux[jj]);
        }
        
        sumflux = sumflux / density;
        sumfluxfract = sumfluxfract + sumflux;
        // ceiling number of particles in cell nodezonein[j]
        pf = ceilf(fabs(sumflux) / weight_p);
        
        //     printf("%5.12e  %d  %5.12e  %5.12e\n", sumflux, pf, fabs(sumflux)/weight_p, density);
        
        if ((j > first_ind) && (j < last_ind)) {
            //calculate distance between nodes
            deltax = (node[nodezonein[j + 1] - 1].coord_xy[0] - node[nodezonein[j - 1] - 1].coord_xy[0]) / 2.0;
            deltay = (node[nodezonein[j + 1] - 1].coord_xy[1] - node[nodezonein[j - 1] - 1].coord_xy[1]) / 2.0;
            //define starting position of first particle
            startpos_x = ((node[nodezonein[j] - 1].coord_xy[0]) - (node[nodezonein[j - 1] - 1].coord_xy[0])) / 2.0 + node[nodezonein[j - 1] - 1].coord_xy[0];
            startpos_y = ((node[nodezonein[j] - 1].coord_xy[1]) - (node[nodezonein[j - 1] - 1].coord_xy[1])) / 2.0 + node[nodezonein[j - 1] - 1].coord_xy[1];
        }
        
        if (j == first_ind) {
            //calculate distance between nodes
            deltax = (node[nodezonein[j + 1] - 1].coord_xy[0] - node[nodezonein[j] - 1].coord_xy[0]) / 2.0;
            deltay = (node[nodezonein[j + 1] - 1].coord_xy[1] - node[nodezonein[j] - 1].coord_xy[1]) / 2.0;
            //define starting position of first particle
            startpos_x = node[nodezonein[j] - 1].coord_xy[0];
            startpos_y = node[nodezonein[j] - 1].coord_xy[1];
        }
        
        if (j == last_ind) {
            //calculate distance between nodes
            deltax = (node[nodezonein[j] - 1].coord_xy[0] - node[nodezonein[j - 1] - 1].coord_xy[0]) / 2.0;
            deltay = (node[nodezonein[j] - 1].coord_xy[1] - node[nodezonein[j - 1] - 1].coord_xy[1]) / 2.0;
            //define starting position of first particle
            startpos_x = node[nodezonein[j - 1] - 1].coord_xy[0];
            startpos_y = node[nodezonein[j - 1] - 1].coord_xy[1];
        }
        
        if (pf < 2) {
            pf = 1;
            eqdist_x = deltax / 2.0;
            eqdist_y = deltay / 2.0;
        } else {
            eqdist_x = deltax / pf;
            eqdist_y = deltay / pf;
        }
        
        for (jj = 0; jj < pf; jj++) {
            particle[k_current].position[0] = startpos_x + eqdist_x * (jj);
            particle[k_current].position[1] = startpos_y + eqdist_y * (jj);
            particle[k_current].velocity[0] = 0.;
            particle[k_current].velocity[1] = 0.;
            particle[k_current].fracture = node[nodezonein[first_ind] - 1].fracture[0];
            particle[k_current].intcell = 0;
            particle[k_current].time = 0.0;
            particle[k_current].fl_weight = weight_p;
            particle[k_current].cell = 0;
            np = k_current;
            k_current++;
            
            if (k_current > npart * 3) {
//                   printf("\n Number of particles with allocated memory (%d) is less than number of particles set up initially (%d).  \n", k_current, npart);
                printf(" Increase the number of particles. Program is terminated. \n");
                exit(1);
            }
        }
    }
    
    return k_current;
}
////////////////////////////////////////////////////////////////////////////

