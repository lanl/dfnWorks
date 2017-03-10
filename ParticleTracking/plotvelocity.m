function plotvelocity(numbfract);
dd=load('plot_vel');
nd=load('fract_nodes');
nf=nd(1);

    a=1;
    b=0;

    for i=1:nf 
a=b+1;
b=b+nd(i+1);
 if i==numbfract || numbfract==0
figure(i)

scatter(dd(a:b,1),dd(a:b,2),5,dd(a:b,5),'o','LineWidth',3.5);

colorbar;
%caxis([4.998 5]);
%caxis([0 0.4e-26]);
hold on
quiver(dd(a:b,1),dd(a:b,2),dd(a:b,3),dd(a:b,4),2.5,'k-','LineWidth',1)
hold on
 end

    end
  
