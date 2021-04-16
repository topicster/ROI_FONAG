%% SCRIPT TO CALCULATE FONAG'S ROI
%
% This script follows a workflow that process the hydrological and economic
% data from FONAG–EPMAPS analysos. It processes hydrological benefits from
% the two scenarios (BAU and SEM) and calculated de return-on-investment
% (ROI) of EPMAPS in FONAG and create plots.
% 
% Boris Ochoa Tocachi
% ATUK Consultoría Estratégica
% Created in April, 2021
% Last edited in April, 2021

close all
clear
clc
disp('CUSTOM SCRIPT TO CALCULATE FONAG''S ROI')

disp(' ')
%% 1. Load BAU-SEM scenario data
disp('1. Loading BAU-SEM scenario data')

% Read the BAU and SEM data
BAU = readtable('BAU_BASE_G_INVERSIONES.csv');
SEM = readtable('SEM_BASE_G_INVERSIONES.csv');

% Read the BAU and SEM data for sensitivity analysis
senbau_BAU = readtable('senbau_BAU_BASE_G_INVERSIONES.csv');
sensem_SEM = readtable('sensem_SEM_BASE_G_INVERSIONES.csv');

disp('Finished loading BAU-SEM scenario data')
%% 2. Calculate investments and benefits
disp('2. Calculate investments and benefits')

% Years
n_years = SEM{:,1};

% Yearly investments
NBS_yearly_investments = SEM{:,5}/1e6;
% Cumulative investments
NBS_cumul_investments = cumsum(NBS_yearly_investments);

% Yearly benefits
BAU_yearly_losses = BAU{:,14}/1e6;
SEM_yearly_benefits = SEM{:,14}/1e6;
GROSS_yearly_benefits = SEM_yearly_benefits - BAU_yearly_losses;
% Cumulative benefits
BAU_cumul_losses = cumsum(BAU_yearly_losses);
SEM_cumul_benefits = cumsum(SEM_yearly_benefits);
GROSS_cumul_benefits = cumsum(GROSS_yearly_benefits);

disp('Finished calculating investments and benefits')
%% 3. Calculate ROI at r=3.46%
disp('3. Calculating ROI at r=3.46%')

% Yearly discounted cashflow
NET_yearly_cashflow = GROSS_yearly_benefits - NBS_yearly_investments;
% Cumulative discounted cashflow
NET_cumul_cashflow = GROSS_cumul_benefits - NBS_cumul_investments;

% ROI
ROI = (GROSS_cumul_benefits - NBS_cumul_investments) ./ NBS_cumul_investments;
ROI(isnan(ROI)) = -1;

% ROI at 2050
ROI2050 = ROI(n_years==2050)*100;

% Net present value
NPV2050 = NET_cumul_cashflow(n_years==2050);

% Payback year
payback_plot = interp1(ROI(10:40),n_years(10:40),0);
payback = n_years(find(ROI>=0,1));

disp('Finished calculating ROI')
%% 4. Discount rate sensitivity analysis
disp('4. Discount rate sensitivity analysis')

% Initialize discount rates
r = [-.01 0 0.01 .0346 0.09];

NPV_factors = (1 + r).^(n_years-2020);
NPV_factors(1:6,:) = 1;

% Yearly investments
norate_NBS_yearly_investments = SEM{:,4}/1e6;
sendis_NBS_yearly_investments = norate_NBS_yearly_investments ./ NPV_factors;
% Cumulative investments
norate_NBS_cumul_investments = cumsum(norate_NBS_yearly_investments);
sendis_NBS_cumul_investments = cumsum(sendis_NBS_yearly_investments);

% Yearly benefits
norate_BAU_yearly_losses = BAU{:,11}/1e6;
norate_SEM_yearly_benefits = SEM{:,11}/1e6;
norate_GROSS_yearly_benefits = norate_SEM_yearly_benefits - norate_BAU_yearly_losses;
sendis_GROSS_yearly_benefits = norate_GROSS_yearly_benefits ./ NPV_factors;

% Cumulative benefits
norate_BAU_cumul_losses = cumsum(norate_BAU_yearly_losses);
norate_SEM_cumul_benefits = cumsum(norate_SEM_yearly_benefits);
norate_GROSS_cumul_benefits = cumsum(norate_GROSS_yearly_benefits);
sendis_GROSS_cumul_benefits = cumsum(sendis_GROSS_yearly_benefits);

% Yearly discounted cashflow
norate_NET_yearly_cashflow = norate_GROSS_yearly_benefits - norate_NBS_yearly_investments;
sendis_NET_yearly_cashflow = norate_NET_yearly_cashflow ./ NPV_factors;
% Cumulative discounted cashflow
norate_NET_cumul_cashflow = norate_GROSS_cumul_benefits - norate_NBS_cumul_investments;
sendis_NET_cumul_cashflow = sendis_GROSS_cumul_benefits - sendis_NBS_cumul_investments;

% ROI
sendis_ROI = (sendis_GROSS_cumul_benefits-sendis_NBS_cumul_investments) ./ sendis_NBS_cumul_investments;
sendis_ROI(isnan(sendis_ROI)) = -1;

% ROI at 2050, net present value, and payback year, 
sendis_ROI2050 = zeros(size(r));
sendis_NPV2050 = zeros(size(r));
sendis_payback = zeros(size(r));
for i = 1:length(r)
    sendis_ROI2050(i) = sendis_ROI(n_years==2050,i)*100;
    sendis_NPV2050(i) = sendis_NET_cumul_cashflow(n_years==2050,i);
    sendis_payback(i) = n_years(find(sendis_ROI(:,i)>=0,1));
end

disp('Finished discount rate sensitivity analysis')
%% 5. Declining discount rate analysis
disp('5. Declining discount rate analysis')

% Instead of using a negative discount rate, use a declining discount rate.

% Consider the discount rate reduces linearly to 0.5% from 2021 to 2054
ddr = linspace(r(4),0.005,n_years(end)-n_years(6))';
ddr = [zeros(6,1) ; ddr];
senddr_NPV_factors = cumprod(1+ddr);

% Yearly investments
senddr_NBS_yearly_investments = norate_NBS_yearly_investments ./ senddr_NPV_factors;
% Cumulative investments
senddr_NBS_cumul_investments = cumsum(senddr_NBS_yearly_investments);

% Yearly benefits
senddr_GROSS_yearly_benefits = norate_GROSS_yearly_benefits ./ senddr_NPV_factors;

% Cumulative benefits
senddr_GROSS_cumul_benefits = cumsum(senddr_GROSS_yearly_benefits);

% Yearly discounted cashflow
senddr_NET_yearly_cashflow = norate_NET_yearly_cashflow ./ senddr_NPV_factors;
% Cumulative discounted cashflow
senddr_NET_cumul_cashflow = senddr_GROSS_cumul_benefits - senddr_NBS_cumul_investments;

% ROI
senddr_ROI = (senddr_GROSS_cumul_benefits-senddr_NBS_cumul_investments) ./ senddr_NBS_cumul_investments;
senddr_ROI(isnan(senddr_ROI)) = -1;

% ROI at 2050
senddr_ROI2050 = senddr_ROI(n_years==2050)*100;

% Net present value
senddr_NPV2050 = senddr_NET_cumul_cashflow(n_years==2050);

% Payback year
senddr_payback = n_years(find(senddr_ROI>=0,1));

disp('Finished declining discount rate analysis')
%% 5. Assuming BAU effects occur at 10 years instead of 20 years
disp('5. Assuming BAU effects occur at 10 years instead of 20 years')

% Assuming BAU effects at 10 years instead of 20 years
% Yearly benefits
senbau_BAU_yearly_losses = senbau_BAU{:,14}/1e6;
senbau_GROSS_yearly_benefits = SEM_yearly_benefits - senbau_BAU_yearly_losses;
% Cumulative benefits
senbau_BAU_cumul_losses = cumsum(senbau_BAU_yearly_losses);
senbau_GROSS_cumul_benefits = cumsum(senbau_GROSS_yearly_benefits);

% Yearly discounted cashflow
senbau_NET_yearly_cashflow = senbau_GROSS_yearly_benefits - NBS_yearly_investments;
% Cumulative discounted cashflow
senbau_NET_cumul_cashflow = senbau_GROSS_cumul_benefits - NBS_cumul_investments;

% ROI
senbau_ROI = (senbau_GROSS_cumul_benefits-NBS_cumul_investments) ./ NBS_cumul_investments;
senbau_ROI(isnan(senbau_ROI)) = -1;

% ROI at 2050
senbau_ROI2050 = senbau_ROI(n_years==2050)*100;

% Net present value
senbau_NPV2050 = senbau_NET_cumul_cashflow(n_years==2050);

% Payback year
senbau_payback = n_years(find(senbau_ROI>=0,1));

disp('Finished assuming BAU effects occur at 10 years instead of 20 years')
%% 6. Assuming SEM effects occur at 20 years instead of 5 years
disp('6. Assuming SEM effects occur at 20 years instead of 5 years')

% Yearly benefits
sensem_SEM_yearly_utilities = sensem_SEM{:,14}/1e6;
sensem_SEM_yearly_benefits = sensem_SEM{:,14}/1e6;
sensem_GROSS_yearly_benefits = sensem_SEM_yearly_benefits - BAU_yearly_losses;
% Cumulative benefits
sensem_SEM_cumul_benefits = cumsum(sensem_SEM_yearly_benefits);
sensem_GROSS_cumul_benefits = cumsum(sensem_GROSS_yearly_benefits);

% Yearly discounted cashflow
sensem_NET_yearly_cashflow = sensem_GROSS_yearly_benefits - NBS_yearly_investments;
% Cumulative discounted cashflow
sensem_NET_cumul_cashflow = sensem_GROSS_cumul_benefits - NBS_cumul_investments;

% ROI
sensem_ROI = (sensem_GROSS_cumul_benefits-NBS_cumul_investments) ./ NBS_cumul_investments;
sensem_ROI(isnan(sensem_ROI)) = -1;

% ROI at 2050
sensem_ROI2050 = sensem_ROI(n_years==2050)*100;

% Net present value
sensem_NPV2050 = sensem_NET_cumul_cashflow(n_years==2050);

% Payback year
sensem_payback = n_years(find(sensem_ROI>=0,1));

disp('Finished assuming SEM effects occur at 20 years instead of 5 years')
%% 7. Assuming NBS maintencace costs double')
disp('7. Assuming NBS maintencace costs double')

% Yearly investments
sennbs_NBS_yearly_investments = 2*SEM{:,5}/1e6;
% Cumulative investments
sennbs_NBS_cumul_investments = cumsum(sennbs_NBS_yearly_investments);

% Yearly discounted cashflow
sennbs_NET_yearly_cashflow = GROSS_yearly_benefits - sennbs_NBS_yearly_investments;
% Cumulative discounted cashflow
sennbs_NET_cumul_cashflow = GROSS_cumul_benefits - sennbs_NBS_cumul_investments;

% ROI
sennbs_ROI = (GROSS_cumul_benefits-sennbs_NBS_cumul_investments) ./ sennbs_NBS_cumul_investments;
sennbs_ROI(isnan(sennbs_ROI)) = -1;

% ROI at 2050
sennbs_ROI2050 = sennbs_ROI(n_years==2050)*100;

% Net present value
sennbs_NPV2050 = sennbs_NET_cumul_cashflow(n_years==2050);

% Payback year
sennbs_payback = n_years(find(sennbs_ROI>=0,1));

disp('Finished assuming NBS maintenance costs double')
%% 8. Assuming water tariff do not increase
disp('8. Assuming water tariff do not increase')

% Yearly benefits
% Yearly benefits
senwat_BAU_yearly_losses = BAU{:,14}/1e6 - BAU{:,12}/1e6 + BAU{:,6}./NPV_factors(:,4)/1e6;
senwat_SEM_yearly_benefits = SEM{:,14}/1e6 - SEM{:,12}/1e6 + SEM{:,6}./NPV_factors(:,4)/1e6;
senwat_GROSS_yearly_benefits = senwat_SEM_yearly_benefits - senwat_BAU_yearly_losses;
% Cumulative benefits
senwat_BAU_cumul_losses = cumsum(senwat_BAU_yearly_losses);
senwat_SEM_cumul_benefits = cumsum(senwat_SEM_yearly_benefits);
senwat_GROSS_cumul_benefits = cumsum(senwat_GROSS_yearly_benefits);

% Yearly discounted cashflow
senwat_NET_yearly_cashflow = senwat_GROSS_yearly_benefits - NBS_yearly_investments;
% Cumulative discounted cashflow
senwat_NET_cumul_cashflow = senwat_GROSS_cumul_benefits - NBS_cumul_investments;

% ROI
senwat_ROI = (senwat_GROSS_cumul_benefits-NBS_cumul_investments) ./ NBS_cumul_investments;
senwat_ROI(isnan(senwat_ROI)) = -1;

% ROI at 2050
senwat_ROI2050 = senwat_ROI(n_years==2050)*100;

% Net present value
senwat_NPV2050 = senwat_NET_cumul_cashflow(n_years==2050);

% Payback year
senwat_payback = n_years(find(senwat_ROI>=0,1));

disp('Finished assuming water tariff do not increase')
%% 9. Plot financial performance
disp('9. Plotting financial performance')

% Initialise variables
offset_loc = 1.2; % To locate plot texts and scale axis

% Plot
ROI_Fig5 = figure;
set(ROI_Fig5,'Renderer','painters')

% Yearly benefits
subplot(3,1,1)
hold on
plot([2010 2060],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
a = bar(n_years, SEM_yearly_benefits,'EdgeColor','none',...
    'FaceColor',[0 0.498039215803146 0],...
    'BarWidth',0.8,'DisplayName','SEM scenario gains');
b = bar(n_years, BAU_yearly_losses,'EdgeColor','none',...
    'FaceColor',[0.850980401039124 0.325490206480026 0.0980392172932625],...
    'BarWidth',0.8,'DisplayName','BAU scenario losses');
c = bar(n_years, -NBS_yearly_investments,'EdgeColor','none',...
    'FaceColor',[0.929411768913269 0.694117665290833 0.125490203499794],...
    'BarWidth',0.5,'DisplayName','NBS intervention costs');
bar(n_years(1:6), -NBS_yearly_investments(1:6),'EdgeColor','none',...
    'FaceColor',[0.929411768913269 0.694117665290833 0.125490203499794],...
    'BarWidth',0.8,'DisplayName','NBS intervention costs');
% Plot auxiliaries
plot([2020.5 2020.5],[-3 1.3],':','Color',[0 0 0])
plot([2040.5 2040.5],[-3 1],':','Color',[0 0 0])
plot([2010 2020.5],[1.3 1.3],':','Color',[0 0 0],'Linewidth',1)
plot([2020.5 2060],[1.3 1.3],'Color',[0 0 0],'LineWidth',2)
plot([2020.5 2040.5],[1 1],'Color',[0 0 0],'LineWidth',2)
text(2016,1.45,'Implementation','HorizontalAlignment','left')
text(2037.5,1.45,'Maintenance','HorizontalAlignment','center')
text(2030.5,1.15,'Scenario development','HorizontalAlignment','center')
% Plot settings
set(gca,'Xlim',[2015 2055],'Ylim',[-2.6 1.4],...
    'YGrid','on','TickDir','out',...
    'TitleHorizontalAlignment','left')
box off
% Labels
xlabel('Year')
ylabel('USD millions (NPV 2020, r = 3.46%)')
% title('Scenario cost-benefit analysis')
legend([a,b,c])
legend('location','southeast')
legend('boxoff')
text(-0.1,1.05,'a','Units','normalized','FontWeight','bold','FontSize',16)

% Financial performance
subplot(3,1,2)
hold on
plot([2010 2060],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
d = plot(n_years(1:36), GROSS_cumul_benefits(1:36),'LineWidth',1.5,...
    'DisplayName','Cumulative gross benefits',...
    'Color',[0 0.447058826684952 0.74117648601532]);
plot(n_years(36:40), GROSS_cumul_benefits(36:40),'--','LineWidth',1.5,...
    'Color',[0 0.447058826684952 0.74117648601532]);
e = plot(n_years(1:36), NET_cumul_cashflow(1:36),'LineWidth',1.5,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078],...
    'DisplayName','Discounted cash flow');
plot(n_years(36:40), NET_cumul_cashflow(36:40),'--','LineWidth',1.5,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078]);
f = plot(n_years(1:36), -NBS_cumul_investments(1:36),'LineWidth',1.5,...
    'Color',[0.929411768913269 0.694117665290833 0.125490203499794],...
    'DisplayName','Cumulative NBS investments');
plot(n_years(36:40), -NBS_cumul_investments(36:40),'--','LineWidth',1.5,...
    'Color',[0.929411768913269 0.694117665290833 0.125490203499794]);
g = bar(2020, NPV2050,...
    'FaceColor',[0.501960813999176 0.501960813999176 0.501960813999176],...
    'EdgeColor','none','BarWidth',0.5,...
    'DisplayName','Net present value (2021–2050)');
% Plot auxiliaries
plot([n_years(36) n_years(36)],[-30 NPV2050],':','Color',[0 0 0])
plot([2020 n_years(36)],[NPV2050 NPV2050],':','Color',[0 0 0])
NPV2050str = num2str(round(NPV2050*100)/100);
text(2021,0.9*NPV2050,NPV2050str,'HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[2015 2055],'Ylim',[-22 47],...
    'YGrid','on','TickDir','out',...
    'TitleHorizontalAlignment','left')
box off
% Labels
xlabel('Year')
ylabel('USD millions (NPV 2020, r = 3.46%)')
% title('Financial performance')
legend([g,d,f,e])
legend('location','northwest')
legend('boxoff')
text(-0.1,1.05,'b','Units','normalized','FontWeight','bold','FontSize',16)

% Plot ROI
subplot(3,1,3)
hold on
plot([2010 2060],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
patch([n_years(:,1);n_years(end:-1:1)],[senbau_ROI;sendis_ROI(end:-1:1,end)],...
    [0.494117647409439 0.184313729405403 0.556862771511078],'Edgecolor','none','FaceAlpha',.25)
h = plot(n_years(1:36),ROI(1:36),'LineWidth',1.5,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078],...
    'DisplayName','Return on investment');
plot(n_years(36:40),ROI(36:40),'--','LineWidth',1.5,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078],...
    'DisplayName','Return on investment');
% Plot auxiliaries
plot([2020 2020],[-5 5],':','Color',[0 0 0])
plot([payback_plot payback_plot],[-5 5],':','Color',[0 0 0])
plot([2020 payback_plot],[2.25 2.25],':','Color',[0 0 0],'Linewidth',1)
plot([payback_plot 2060],[2.25 2.25],'Color',[0 0 0],'LineWidth',2)
text((payback_plot+2020)/2,2.4,'Payback',...
    'HorizontalAlignment','center')
text((2054+payback_plot)/2,2.4,'Profit',...
    'HorizontalAlignment','center')
text(n_years(end),sendis_ROI(end,end)+.1,[' r = ',num2str(100*r(end)),'%'],'HorizontalAlignment','left')
text(n_years(end),sendis_ROI(end,4)+.1,[' r = ',num2str(100*r(4)),'%'],'HorizontalAlignment','left')
text(n_years(end),senbau_ROI(end-2)+.1,' BAU 2030','HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[2015 2055],'Ylim',[-1.1 2.6],...
    'YGrid','on','TickDir','out',...
    'TitleHorizontalAlignment','left')
box off
% Labels
xlabel('Year')
ylabel('ROI = (benefits – investments)/investments')
% title('Return on investment')
legend(h)
legend('location','southeast')
legend('boxoff')
text(-0.1,1.05,'c','Units','normalized','FontWeight','bold','FontSize',16)

% Export Figure
disp('Exporting the Figure to pdf')
% Set the paper size [width height]
set(ROI_Fig5,'PaperSize',[20 40]);
% set(ROI_Fig5,'PaperOrientation','landscape')
print(ROI_Fig5,'ROI_Fig5_export','-dpdf','-fillpage')

disp('Finished plotting ROI Figure')
%% 10. Sensitivity analysis table
disp('10. Sensitivity analysis table')

% Table:     NPV2050            ROI2050             payback
table_ROI = [NPV2050            ROI2050             payback;...
             senbau_NPV2050     senbau_ROI2050      senbau_payback;...
             sensem_NPV2050     sensem_ROI2050      sensem_payback;...
             sennbs_NPV2050     sennbs_ROI2050      sennbs_payback;...
             senwat_NPV2050     senwat_ROI2050      senwat_payback;...
             sendis_NPV2050(5)  sendis_ROI2050(5)   sendis_payback(5);...
             senddr_NPV2050     senddr_ROI2050      senddr_payback];

% Plot multiple ROI
ROI_Fig6 = figure;
set(ROI_Fig6,'Renderer','painters')
plot([2010 2060],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
hold on
roi1 = plot(n_years,ROI,'LineWidth',2,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078],...
    'DisplayName','Original assumptions');
roi2 = plot(n_years,senbau_ROI,'LineWidth',1,...
    'DisplayName','Degradation peaks in 2030');
roi3 = plot(n_years,sensem_ROI,'LineWidth',1,...
    'DisplayName','Full-size NBS effects peak in 2040');
roi4 = plot(n_years,sennbs_ROI,'LineWidth',1,...
    'DisplayName','NBS maintenance costs double');
roi5 = plot(n_years,senwat_ROI,'LineWidth',1,...
    'DisplayName','Water tariff does not increase');
roi6 = plot(n_years,sendis_ROI(:,5),'LineWidth',1,...
    'DisplayName','Higher 9% discount rate');
roi7 = plot(n_years,senddr_ROI,'LineWidth',1,...
    'DisplayName','Declining discount rate');
roi8 = plot(n_years,sendis_ROI(:,2),'LineWidth',1,...
    'DisplayName','Zero 0% discount rate');
% Plot settings
set(gca,'Xlim',[2015 2055],'Ylim',[-1.1 3.2],...
    'YGrid','on','TickDir','out',...
    'TitleHorizontalAlignment','left')
box off
% Labels
xlabel('Year')
ylabel('ROI = (benefits – investments)/investments')
% title('Return on investment')
legend([roi8,roi2,roi7,roi1,roi3,roi5,roi4,roi6])
legend('location','northwest')
legend('boxoff')

% Export Figure
disp('Exporting the Figure to pdf')
% Set the paper size [width height]
set(ROI_Fig6,'PaperSize',[20 20]);
% set(ROI_Fig6,'PaperOrientation','landscape')
print(ROI_Fig6,'ROI_Fig6_export','-dpdf','-fillpage')

disp('Finished sensitivity analysis table')
%% 11. Save results
disp('11. Saving results')

clear a b c d e f g h NPV2054str
clear roi1 roi2 roi3 roi4 roi5 roi6 roi7 roi8
clear ROI_Fig5 ROI_Fig6

save ROI_FONAG

disp('Finished saving results')