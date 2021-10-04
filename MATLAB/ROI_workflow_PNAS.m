%% SCRIPT TO CALCULATE FONAG'S ROI
%
% This script follows a workflow that process the hydrological and economic
% data from FONAG–EPMAPS analysos. It processes hydrological benefits from
% the two scenarios (BAU and NBS) and calculated de return-on-investment
% (ROI) of EPMAPS in FONAG and create plots.
% 
% Boris Ochoa Tocachi
% ATUK Consultoría Estratégica
% Created in April, 2021
% Last edited in July, 2021

close all
clear
clc
disp('CUSTOM SCRIPT TO CALCULATE FONAG''S ROI')

disp(' ')
%% 1. Load BAU-NBS scenario data
disp('1. Loading BAU-NBS scenario data')

% Read the BAU and NBS water volume data
BAU_VOL = readtable('superficial/superficial_BAU-BASE_HIP-1_VOLUMEN.csv');
NBS_BAU_VOL = readtable('superficial/superficial_SEMBAU-BASE_VOLUMEN.csv');
NBS_BASE_VOL = readtable('superficial/superficial_SEMBASE-BASE_HIP-1_VOLUMEN.csv');
NBS_VOL = NBS_BAU_VOL;
NBS_VOL{:,2:16} = NBS_BAU_VOL{:,2:16} + NBS_BASE_VOL{:,2:16};

% Read the BAU and NBS hydrologic benefit data
BAU_BHI = readtable('superficial/superficial_BAU-BASE_HIP-1_BHIDRICOS.csv');
NBS_BASE_BHI = readtable('superficial/superficial_SEMBASE-BASE_HIP-1_BHIDRICOS.csv');
NBS_BAU_BHI = readtable('superficial/superficial_SEMBAU-BASE_BHIDRICOS.csv');
NBS_BHI = NBS_BAU_BHI;
NBS_BHI{:,2:end} = NBS_BAU_BHI{:,2:end} + NBS_BASE_BHI{:,2:end};

% Read the BAU and NBS economic data
BAU_ECO = readtable('superficial/superficial_BAU-BASE_HIP-1_INVERSIONES.csv');
NBS_BASE_ECO = readtable('superficial/superficial_SEMBASE-BASE_HIP-1_INVERSIONES.csv');
NBS_BAU_ECO = readtable('superficial/superficial_SEMBAU-BASE_INVERSIONES.csv');
NBS_ECO = NBS_BAU_ECO;
NBS_ECO{:,6:end} = NBS_BAU_ECO{:,6:end} + NBS_BASE_ECO{:,6:end};

% Read the BAU and NBS economic data for sensitivity analysis
senbau_BAU_ECO = readtable('superficial/superficial_BAU-BASE_HIP-Alt_INVERSIONES.csv');
sennbs_BASE_ECO = readtable('superficial/superficial_SEMBASE-BASE_HIP-Alt_INVERSIONES.csv');
sennbs_NBS_ECO = NBS_BAU_ECO;
sennbs_NBS_ECO{:,6:end} = NBS_BAU_ECO{:,6:end} + sennbs_BASE_ECO{:,6:end};

sennbs2_BASE_ECO = readtable('superficial/superficial_SEMBASE-BASE_HIP-Alt-2_INVERSIONES_2.csv');
sennbs2_NBS_ECO = NBS_BAU_ECO;
sennbs2_NBS_ECO{:,6:end} = NBS_BAU_ECO{:,6:end} + sennbs2_BASE_ECO{:,6:end};

disp('Finished loading BAU-NBS scenario data')
%% 2. Calculate investments and benefits
disp('2. Calculate investments and benefits')

% Years
n_years = NBS_ECO{:,1};

% Hydrological benefits
BAU_BASE_hydro_diff = sum(BAU_BHI{:,2:5},2)/1e6;
NBS_BASE_hydro_diff = sum(NBS_BHI{:,2:5},2)/1e6;

% Yearly investments
NBS_yearly_investments = NBS_ECO{:,5}/1e6;
% Cumulative investments
NBS_cumul_investments = cumsum(NBS_yearly_investments);

% Yearly benefits
BAU_yearly_losses = BAU_ECO{:,21}/1e6;
NBS_yearly_benefits = NBS_ECO{:,21}/1e6;
GROSS_yearly_benefits = NBS_yearly_benefits - BAU_yearly_losses;
% Cumulative benefits
BAU_cumul_losses = cumsum(BAU_yearly_losses);
NBS_cumul_benefits = cumsum(NBS_yearly_benefits);
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

% ROI at 2080
ROI2080 = ROI(n_years==2080)*100;

% Net present value
NPV2080 = NET_cumul_cashflow(n_years==2080);

% Payback year
payback_plot = interp1(ROI(10:40),n_years(10:40),0);
if isempty(n_years(find(ROI>=0,1)))
    payback = NaN;
else
    payback = n_years(find(ROI>=0,1));
end

disp('Finished calculating ROI')
%% 4. Discount rate sensitivity analysis
disp('4. Discount rate sensitivity analysis')

% Initialize discount rates
sendis_r = [-.01 0 0.01 .0346 0.09];

NPV_factors = (1 + sendis_r).^(n_years-2020);
NPV_factors(1:6,:) = 1;

% Yearly investments
norate_NBS_yearly_investments = NBS_ECO{:,4}/1e6;
sendis_NBS_yearly_investments = norate_NBS_yearly_investments ./ NPV_factors;
% Cumulative investments
norate_NBS_cumul_investments = cumsum(norate_NBS_yearly_investments);
sendis_NBS_cumul_investments = cumsum(sendis_NBS_yearly_investments);

% Yearly benefits
norate_BAU_yearly_losses = BAU_ECO{:,17}/1e6;
norate_NBS_yearly_benefits = NBS_ECO{:,17}/1e6;
norate_GROSS_yearly_benefits = norate_NBS_yearly_benefits - norate_BAU_yearly_losses;
sendis_BAU_yearly_losses = norate_BAU_yearly_losses ./ NPV_factors;
sendis_NBS_yearly_benefits = norate_NBS_yearly_benefits ./ NPV_factors;
sendis_GROSS_yearly_benefits = norate_GROSS_yearly_benefits ./ NPV_factors;

% Cumulative benefits
norate_BAU_cumul_losses = cumsum(norate_BAU_yearly_losses);
norate_NBS_cumul_benefits = cumsum(norate_NBS_yearly_benefits);
norate_GROSS_cumul_benefits = cumsum(norate_GROSS_yearly_benefits);
sendis_BAU_cumul_losses = cumsum(norate_BAU_cumul_losses);
sendis_NBS_cumul_benefits = cumsum(norate_NBS_cumul_benefits);
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

% ROI at 2080, net present value, and payback year, 
sendis_ROI2080 = zeros(size(sendis_r));
sendis_NPV2080 = zeros(size(sendis_r));
sendis_payback = zeros(size(sendis_r));
for i = 1:length(sendis_r)
    sendis_ROI2080(i) = sendis_ROI(n_years==2080,i)*100;
    sendis_NPV2080(i) = sendis_NET_cumul_cashflow(n_years==2080,i);
    sendis_find = find(sendis_ROI(:,i)>=0,1);
    if isempty(sendis_find)
        sendis_payback(i) = NaN;
    else
        sendis_payback(i) = n_years(sendis_find);
    end
end

disp('Finished discount rate sensitivity analysis')
%% 5. Declining discount rate analysis
disp('5. Declining discount rate analysis')

% Instead of using a negative discount rate, use a declining discount rate.

% Consider the discount rate reduces linearly to 0.5% from 2021 to 2080
ddr = linspace(sendis_r(4),0.005,n_years(end)-n_years(6))';
ddr = [zeros(6,1) ; ddr];
senddr_NPV_factors = cumprod(1+ddr);

% Yearly investments
senddr_NBS_yearly_investments = norate_NBS_yearly_investments ./ senddr_NPV_factors;
% Cumulative investments
senddr_NBS_cumul_investments = cumsum(senddr_NBS_yearly_investments);

% Yearly benefits
senddr_BAU_yearly_losses = norate_BAU_yearly_losses ./ senddr_NPV_factors;
senddr_NBS_yearly_benefits = norate_NBS_yearly_benefits ./ senddr_NPV_factors;
senddr_GROSS_yearly_benefits = norate_GROSS_yearly_benefits ./ senddr_NPV_factors;

% Cumulative benefits
senddr_BAU_cumul_losses = cumsum(senddr_BAU_yearly_losses);
senddr_NBS_cumul_benefits = cumsum(senddr_NBS_yearly_benefits);
senddr_GROSS_cumul_benefits = cumsum(senddr_GROSS_yearly_benefits);

% Yearly discounted cashflow
senddr_NET_yearly_cashflow = norate_NET_yearly_cashflow ./ senddr_NPV_factors;
% Cumulative discounted cashflow
senddr_NET_cumul_cashflow = senddr_GROSS_cumul_benefits - senddr_NBS_cumul_investments;

% ROI
senddr_ROI = (senddr_GROSS_cumul_benefits-senddr_NBS_cumul_investments) ./ senddr_NBS_cumul_investments;
senddr_ROI(isnan(senddr_ROI)) = -1;

% ROI at 2080
senddr_ROI2080 = senddr_ROI(n_years==2080)*100;

% Net present value
senddr_NPV2080 = senddr_NET_cumul_cashflow(n_years==2080);

% Payback year
if isempty(n_years(find(senddr_ROI>=0,1)))
    senddr_payback = NaN;
else
    senddr_payback = n_years(find(senddr_ROI>=0,1));
end

disp('Finished declining discount rate analysis')
%% 6. Assuming BAU effects occur at twice the pace
disp('6. Assuming BAU effects occur at twice the pace')

% Assuming BAU effects at twice the pace
% Yearly benefits
senbau_BAU_yearly_losses = senbau_BAU_ECO{:,21}/1e6;
senbau_GROSS_yearly_benefits = NBS_yearly_benefits - senbau_BAU_yearly_losses;
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

% ROI at 2080
senbau_ROI2080 = senbau_ROI(n_years==2080)*100;

% Net present value
senbau_NPV2080 = senbau_NET_cumul_cashflow(n_years==2080);

% Payback year
if isempty(n_years(find(senbau_ROI>=0,1)))
    senbau_payback = NaN;
else
    senbau_payback = n_years(find(senbau_ROI>=0,1));
end

% Assuming BAU effects at half the pace
% Yearly benefits
senbau2_BAU_yearly_losses = BAU_ECO{:,21}/1e6/2;
senbau2_GROSS_yearly_benefits = NBS_yearly_benefits - senbau2_BAU_yearly_losses;
% Cumulative benefits
senbau2_BAU_cumul_losses = cumsum(senbau2_BAU_yearly_losses);
senbau2_GROSS_cumul_benefits = cumsum(senbau2_GROSS_yearly_benefits);

% Yearly discounted cashflow
senbau2_NET_yearly_cashflow = senbau2_GROSS_yearly_benefits - NBS_yearly_investments;
% Cumulative discounted cashflow
senbau2_NET_cumul_cashflow = senbau2_GROSS_cumul_benefits - NBS_cumul_investments;

% ROI
senbau2_ROI = (senbau2_GROSS_cumul_benefits-NBS_cumul_investments) ./ NBS_cumul_investments;
senbau2_ROI(isnan(senbau2_ROI)) = -1;

% ROI at 2080
senbau2_ROI2080 = senbau2_ROI(n_years==2080)*100;

% Net present value
senbau2_NPV2080 = senbau2_NET_cumul_cashflow(n_years==2080);

% Payback year
if isempty(n_years(find(senbau2_ROI>=0,1)))
    senbau2_payback = NaN;
else
    senbau2_payback = n_years(find(senbau2_ROI>=0,1));
end

disp('Finished assuming BAU effects occur at 10 years instead of 20 years')
%% 7. Assuming NBS effects occur at 20 years instead of 10 years
disp('7. Assuming NBS effects occur at 20 years instead of 10 years')

% Assuming NBS effects occur at 20 years
% Yearly benefits
sennbs_NBS_yearly_benefits = sennbs_NBS_ECO{:,21}/1e6;
sennbs_GROSS_yearly_benefits = sennbs_NBS_yearly_benefits - BAU_yearly_losses;
% Cumulative benefits
sennbs_NBS_cumul_benefits = cumsum(sennbs_NBS_yearly_benefits);
sennbs_GROSS_cumul_benefits = cumsum(sennbs_GROSS_yearly_benefits);

% Yearly discounted cashflow
sennbs_NET_yearly_cashflow = sennbs_GROSS_yearly_benefits - NBS_yearly_investments;
% Cumulative discounted cashflow
sennbs_NET_cumul_cashflow = sennbs_GROSS_cumul_benefits - NBS_cumul_investments;

% ROI
sennbs_ROI = (sennbs_GROSS_cumul_benefits-NBS_cumul_investments) ./ NBS_cumul_investments;
sennbs_ROI(isnan(sennbs_ROI)) = -1;

% ROI at 2080
sennbs_ROI2080 = sennbs_ROI(n_years==2080)*100;

% Net present value
sennbs_NPV2080 = sennbs_NET_cumul_cashflow(n_years==2080);

% Payback year
if isempty(n_years(find(sennbs_ROI>=0,1)))
    sennbs_payback = NaN;
else
    sennbs_payback = n_years(find(sennbs_ROI>=0,1));
end

% Assuming NBS effects occur at 5 years

% Yearly benefits
sennbs2_NBS_yearly_benefits = sennbs2_NBS_ECO{:,21}/1e6;
sennbs2_GROSS_yearly_benefits = sennbs2_NBS_yearly_benefits - BAU_yearly_losses;
% Cumulative benefits
sennbs2_NBS_cumul_benefits = cumsum(sennbs2_NBS_yearly_benefits);
sennbs2_GROSS_cumul_benefits = cumsum(sennbs2_GROSS_yearly_benefits);

% Yearly discounted cashflow
sennbs2_NET_yearly_cashflow = sennbs2_GROSS_yearly_benefits - NBS_yearly_investments;
% Cumulative discounted cashflow
sennbs2_NET_cumul_cashflow = sennbs2_GROSS_cumul_benefits - NBS_cumul_investments;

% ROI
sennbs2_ROI = (sennbs2_GROSS_cumul_benefits-NBS_cumul_investments) ./ NBS_cumul_investments;
sennbs2_ROI(isnan(sennbs2_ROI)) = -1;

% ROI at 2080
sennbs2_ROI2080 = sennbs2_ROI(n_years==2080)*100;

% Net present value
sennbs2_NPV2080 = sennbs2_NET_cumul_cashflow(n_years==2080);

% Payback year
if isempty(n_years(find(sennbs2_ROI>=0,1)))
    sennbs2_payback = NaN;
else
    sennbs2_payback = n_years(find(sennbs2_ROI>=0,1));
end

disp('Finished assuming NBS effects occur at 20 years instead of 5 years')
%% 8. Assuming NBS maintencace costs 50% more')
disp('8. Assuming NBS maintencace costs 50% more')

% Assuming NBS maintencace costs 50% more
% Yearly investments
senman_NBS_yearly_investments = NBS_ECO{:,5}/1e6;
senman_NBS_yearly_investments(7:end) = 1.5*senman_NBS_yearly_investments(7:end);
% Cumulative investments
senman_NBS_cumul_investments = cumsum(senman_NBS_yearly_investments);

% Yearly discounted cashflow
senman_NET_yearly_cashflow = GROSS_yearly_benefits - senman_NBS_yearly_investments;
% Cumulative discounted cashflow
senman_NET_cumul_cashflow = GROSS_cumul_benefits - senman_NBS_cumul_investments;

% ROI
senman_ROI = (GROSS_cumul_benefits-senman_NBS_cumul_investments) ./ senman_NBS_cumul_investments;
senman_ROI(isnan(senman_ROI)) = -1;

% ROI at 2080
senman_ROI2080 = senman_ROI(n_years==2080)*100;

% Net present value
senman_NPV2080 = senman_NET_cumul_cashflow(n_years==2080);

% Payback year
if isempty(n_years(find(senman_ROI>=0,1)))
    senman_payback = NaN;
else
    senman_payback = n_years(find(senman_ROI>=0,1));
end

% Assuming NBS maintencace costs 50% less
% Yearly investments
senman2_NBS_yearly_investments = NBS_ECO{:,5}/1e6;
senman2_NBS_yearly_investments(7:end) = 0.5*senman_NBS_yearly_investments(7:end);
% Cumulative investments
senman2_NBS_cumul_investments = cumsum(senman2_NBS_yearly_investments);

% Yearly discounted cashflow
senman2_NET_yearly_cashflow = GROSS_yearly_benefits - senman2_NBS_yearly_investments;
% Cumulative discounted cashflow
senman2_NET_cumul_cashflow = GROSS_cumul_benefits - senman2_NBS_cumul_investments;

% ROI
senman2_ROI = (GROSS_cumul_benefits-senman2_NBS_cumul_investments) ./ senman2_NBS_cumul_investments;
senman2_ROI(isnan(senman2_ROI)) = -1;

% ROI at 2080
senman2_ROI2080 = senman2_ROI(n_years==2080)*100;

% Net present value
senman2_NPV2080 = senman2_NET_cumul_cashflow(n_years==2080);

% Payback year
if isempty(n_years(find(senman2_ROI>=0,1)))
    senman2_payback = NaN;
else
    senman2_payback = n_years(find(senman2_ROI>=0,1));
end

disp('Finished assuming NBS maintenance costs double')
%% 9. Assuming water tariff increases with inflation
disp('9. Assuming water tariff increases with inflation')

% % Factor of water tariff increases X% every Z years
% X = 5; % Percentage increase in water tariff
% Z = 5; % Number of years for an increase in tariff
% 
% senwat_tariff_factor = ones(size(BAU_ECO{:,6}));
% for i = 2:length(n_years)/Z
%     senwat_tariff_factor(n_years>2020+(i-1)*Z) = ...
%         senwat_tariff_factor(n_years>2020+(i-1)*Z) * (1+X/100);
% end
% senwat_BAU_yearly_losses = BAU_ECO{:,21}/1e6 - BAU_ECO{:,9}/1e6 + BAU_ECO{:,7}.*senwat_tariff_factor/1e6;
% senwat_NBS_yearly_benefits = NBS_ECO{:,21}/1e6 - NBS_ECO{:,9}/1e6 + NBS_ECO{:,7}.*senwat_tariff_factor/1e6;

% Assuming water tariff increases with inflation
% Yearly benefits
senwat_BAU_yearly_losses = BAU_ECO{:,21}/1e6 - BAU_ECO{:,9}/1e6 + BAU_ECO{:,7}.*NPV_factors(:,3)/1e6;
senwat_NBS_yearly_benefits = NBS_ECO{:,21}/1e6 - NBS_ECO{:,9}/1e6 + NBS_ECO{:,7}.*NPV_factors(:,3)/1e6;
senwat_GROSS_yearly_benefits = senwat_NBS_yearly_benefits - senwat_BAU_yearly_losses;
% Cumulative benefits
senwat_BAU_cumul_losses = cumsum(senwat_BAU_yearly_losses);
senwat_NBS_cumul_benefits = cumsum(senwat_NBS_yearly_benefits);
senwat_GROSS_cumul_benefits = cumsum(senwat_GROSS_yearly_benefits);

% Yearly discounted cashflow
senwat_NET_yearly_cashflow = senwat_GROSS_yearly_benefits - NBS_yearly_investments;
% Cumulative discounted cashflow
senwat_NET_cumul_cashflow = senwat_GROSS_cumul_benefits - NBS_cumul_investments;

% ROI
senwat_ROI = (senwat_GROSS_cumul_benefits-NBS_cumul_investments) ./ NBS_cumul_investments;
senwat_ROI(isnan(senwat_ROI)) = -1;

% ROI at 2080
senwat_ROI2080 = senwat_ROI(n_years==2080)*100;

% Net present value
senwat_NPV2080 = senwat_NET_cumul_cashflow(n_years==2080);

% Payback year
if isempty(n_years(find(senwat_ROI>=0,1)))
    senwat_payback = NaN;
else
    senwat_payback = n_years(find(senwat_ROI>=0,1));
end

% Assuming water tariff does not increase at all
% Yearly benefits
senwat2_BAU_yearly_losses = BAU_ECO{:,21}/1e6 - BAU_ECO{:,9}/1e6 + BAU_ECO{:,7}/1e6;
senwat2_NBS_yearly_benefits = NBS_ECO{:,21}/1e6 - NBS_ECO{:,9}/1e6 + NBS_ECO{:,7}/1e6;
senwat2_GROSS_yearly_benefits = senwat2_NBS_yearly_benefits - senwat2_BAU_yearly_losses;
% Cumulative benefits
senwat2_BAU_cumul_losses = cumsum(senwat2_BAU_yearly_losses);
senwat2_NBS_cumul_benefits = cumsum(senwat2_NBS_yearly_benefits);
senwat2_GROSS_cumul_benefits = cumsum(senwat2_GROSS_yearly_benefits);

% Yearly discounted cashflow
senwat2_NET_yearly_cashflow = senwat2_GROSS_yearly_benefits - NBS_yearly_investments;
% Cumulative discounted cashflow
senwat2_NET_cumul_cashflow = senwat2_GROSS_cumul_benefits - NBS_cumul_investments;

% ROI
senwat2_ROI = (senwat2_GROSS_cumul_benefits-NBS_cumul_investments) ./ NBS_cumul_investments;
senwat2_ROI(isnan(senwat2_ROI)) = -1;

% ROI at 2080
senwat2_ROI2080 = senwat2_ROI(n_years==2080)*100;

% Net present value
senwat2_NPV2080 = senwat2_NET_cumul_cashflow(n_years==2080);

% Payback year
if isempty(n_years(find(senwat2_ROI>=0,1)))
    senwat2_payback = NaN;
else
    senwat2_payback = n_years(find(senwat2_ROI>=0,1));
end

disp('Finished assuming water tariff increases with inflation')
%% 10. Plot financial performance
disp('10. Plotting financial performance')

% Initialise variables
offset_loc = 1.2; % To locate plot texts and scale axis

% Plot
ROI_Fig4 = figure;
set(ROI_Fig4,'Renderer','painters')

% Hydrological differences
subplot(2,1,1)
hold on
plot([datetime(n_years(1)-5,01,01) datetime(n_years(end),01,01)],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
l = plot(NBS_BHI{:,1}-365,NBS_BASE_hydro_diff,'LineWidth',2,...
    'Color',[0 0.498039215803146 0],...
    'DisplayName','NBS–BASE effects');
m = plot(BAU_BHI{:,1}-365,BAU_BASE_hydro_diff,'LineWidth',2,...
    'Color',[0.850980401039124 0.325490206480026 0.0980392172932625],...
    'DisplayName','BAU–BASE effects');
% Plot auxiliaries
plot([datetime(2020,01,01) datetime(2020,01,01)],[-3 2],':','Color',[0 0 0])
plot([datetime(2080,01,01) datetime(2080,01,01)],[-2.8 0],':','Color',[0 0 0])
plot([datetime(2030,01,01) datetime(2030,01,01)],[0 2],':','Color',[0 0 0])
plot([datetime(2020,01,01) datetime(2030,01,01)],[2 2],'Color',[0 0 0],'Linewidth',2)
plot([datetime(2020,01,01) datetime(2080,01,01)],[-2.8 -2.8],'Color',[0 0 0],'LineWidth',2)
text(datetime(2020,01,01),2.2,'NBS peak performance','HorizontalAlignment','left')
text(datetime(2050,01,01),-2.6,'BAU scenario development','HorizontalAlignment','center')
% Plot settings
set(gca,'Xlim',[datetime(n_years(1),01,01) datetime(n_years(end)+1,01,01)],...
    'Ylim',[-3.1 2.1],'TickDir','out')
box off
% Labels
xlabel('Year')
ylabel('Flow (× 10^6 m^3 month^{–1})')
% title('Scenario cost-benefit analysis')
n = legend([l,m]);
legend('location','west')
n_pos = get(n,'Position');
n_pos(1) = 0.21;
n_pos(2) = 0.65;
legend('Position',n_pos)
legend('boxoff')
text(-0.1,1.15,'A','Units','normalized','FontWeight','bold','FontSize',16)

% Yearly benefits
subplot(2,1,2)
hold on
plot([n_years(1)-5 n_years(end)],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
a = bar(n_years, [NBS_yearly_benefits,-BAU_yearly_losses,-NBS_yearly_investments],'stacked','EdgeColor','none',...
    'BarWidth',0.8);

a(1,1).DisplayName = 'NBS scenario expected gains';
a(1,1).FaceColor = [0 0.498039215803146 0];
a(1,2).DisplayName = 'BAU scenario avoided losses';
a(1,2).FaceColor = [0.850980401039124 0.325490206480026 0.0980392172932625];
a(1,3).DisplayName = 'NBS intervention costs';
a(1,3).FaceColor = [0.929411768913269 0.694117665290833 0.125490203499794];

% Plot auxiliaries
plot([2020.5 2020.5],[-3 4],':','Color',[0 0 0])
plot([n_years(1)-5 2020.5],[4 4],':','Color',[0 0 0],'Linewidth',1)
plot([2020.5 n_years(end)],[4 4],'Color',[0 0 0],'LineWidth',2)
text(n_years(1),4.3,' Implementation','HorizontalAlignment','left')
text((n_years(1)+n_years(end))/2,4.3,'Maintenance','HorizontalAlignment','center')
% text(2030.5,1.15,'Scenario development','HorizontalAlignment','center')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+1],'Ylim',[-4.2 4.2],'TickDir','out')
box off
% Labels
xlabel('Year')
ylabel('Annual USD millions (NPV 2020, r = 3.46%)')
% title('Scenario cost-benefit analysis')
n = legend(a);
legend('location','southwest')
n_pos = get(n,'Position');
n_pos(1) = 0.21;
legend('Position',n_pos)
legend('boxoff')
text(-0.1,1.15,'B','Units','normalized','FontWeight','bold','FontSize',16)
% Obtain axes
ax1 = gca;

% Financial performance
ax2 = axes;
hold on
plot([n_years(1)-5 n_years(1)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
d = plot(n_years, GROSS_cumul_benefits,'LineWidth',1.5,...
    'DisplayName','Cumulative gross benefits',...
    'Color',[0 0.447058826684952 0.74117648601532]);
e = plot(n_years, NET_cumul_cashflow,'LineWidth',1.5,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078],...
    'DisplayName','Discounted cash flow');
f = plot(n_years, -NBS_cumul_investments,'LineWidth',1.5,...
    'Color',[0.929411768913269 0.694117665290833 0.125490203499794],...
    'DisplayName','Cumulative NBS investments');
bar(2020, NPV2080,...
    'FaceColor',[0.501960813999176 0.501960813999176 0.501960813999176],...
    'EdgeColor','none','BarWidth',0.5,...
    'DisplayName','Net present value (2021–2080)');
% Plot auxiliaries
plot([n_years(end) n_years(end)],[0 NPV2080],':','Color',[0 0 0])
plot([2020 n_years(end)],[NPV2080 NPV2080],':','Color',[0 0 0])
NPV2080str = ['NPV = ',num2str(round(NPV2080*100)/100)];
text(2021,1.25*NPV2080,NPV2080str,'HorizontalAlignment','center')
% Plot settings
set(ax2,'Position',get(ax1,'Position'),'Color','none',...
    'Xlim',[n_years(1) n_years(end)+1],'Ylim',[-105 105],...
    'YAxisLocation','right','Xticklabel','','TickDir','out')
box off
% Labels
ylabel('Cashflow USD millions (NPV 2020, r = 3.46%)')
% title('Financial performance')
m = legend([d,f,e]);
legend('location','southeast')
m_pos = get(m,'Position');
m_pos(2) = n_pos(2);
legend('Position',m_pos)
legend('boxoff')

% Export Figure
disp('Exporting the Figure to pdf')
% Set the paper size [width height]
set(ROI_Fig4,'PaperSize',[20 20]);
% set(ROI_Fig4,'PaperOrientation','landscape')
print(ROI_Fig4,'PNAS - ROI FONAG - Fig4','-dpdf','-fillpage')

% ALTERNATIVE FIGURE
% Plot
ROI_Fig4alt = figure;
set(ROI_Fig4alt,'Renderer','painters')

% Hydrological differences
subplot(4,1,1)
hold on
plot([datetime(n_years(1)-5,01,01) datetime(n_years(end),01,01)],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
l = plot(NBS_BHI{:,1}-365,NBS_BASE_hydro_diff,'LineWidth',2,...
    'Color',[0 0.498039215803146 0],...
    'DisplayName','NBS–BASE effects');
m = plot(BAU_BHI{:,1}-365,BAU_BASE_hydro_diff,'LineWidth',2,...
    'Color',[0.850980401039124 0.325490206480026 0.0980392172932625],...
    'DisplayName','BAU–BASE effects');
% Plot auxiliaries
plot([datetime(2020,01,01) datetime(2020,01,01)],[-3 2],':','Color',[0 0 0])
plot([datetime(2080,01,01) datetime(2080,01,01)],[-2.8 0],':','Color',[0 0 0])
plot([datetime(2030,01,01) datetime(2030,01,01)],[0 2],':','Color',[0 0 0])
plot([datetime(2020,01,01) datetime(2030,01,01)],[2 2],'Color',[0 0 0],'Linewidth',2)
plot([datetime(2020,01,01) datetime(2080,01,01)],[-2.8 -2.8],'Color',[0 0 0],'LineWidth',2)
text(datetime(2020,01,01),2.2,'NBS peak performance','HorizontalAlignment','left')
text(datetime(2050,01,01),-2.6,'BAU scenario development','HorizontalAlignment','center')
% Plot settings
set(gca,'Xlim',[datetime(n_years(1),01,01) datetime(n_years(end)+1,01,01)],...
    'Ylim',[-3.1 2.1],'TickDir','out')
box off
% Labels
xlabel('Year')
ylabel('Flow (× 10^6 m^3 month^{–1})')
% title('Scenario cost-benefit analysis')
n = legend([l,m]);
legend('location','west')
n_pos = get(n,'Position');
n_pos(1) = 0.23;
n_pos(2) = 0.78;
legend('Position',n_pos)
legend('boxoff')
text(-0.1,1.1,'A','Units','normalized','FontWeight','bold','FontSize',16)

% Yearly benefits
subplot(4,1,2)
hold on
plot([n_years(1)-5 n_years(end)],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
a = bar(n_years, [NBS_yearly_benefits,-BAU_yearly_losses,-NBS_yearly_investments],'stacked','EdgeColor','none',...
    'BarWidth',0.8);

a(1,1).DisplayName = 'NBS scenario expected gains';
a(1,1).FaceColor = [0 0.498039215803146 0];
a(1,2).DisplayName = 'BAU scenario avoided losses';
a(1,2).FaceColor = [0.850980401039124 0.325490206480026 0.0980392172932625];
a(1,3).DisplayName = 'NBS intervention costs';
a(1,3).FaceColor = [0.929411768913269 0.694117665290833 0.125490203499794];

% Plot auxiliaries
plot([2020.5 2020.5],[-3 4],':','Color',[0 0 0])
plot([n_years(1)-5 2020.5],[4 4],':','Color',[0 0 0],'Linewidth',1)
plot([2020.5 n_years(end)],[4 4],'Color',[0 0 0],'LineWidth',2)
text(n_years(1),4.3,' Implementation','HorizontalAlignment','left')
text((n_years(1)+n_years(end))/2,4.3,'Maintenance','HorizontalAlignment','center')
% text(2030.5,1.15,'Scenario development','HorizontalAlignment','center')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+1],'Ylim',[-3.15 4.15],'TickDir','out')
box off
% Labels
xlabel('Year')
ylabel('USD millions (NPV 2020, r = 3.46%)')
% title('Scenario cost-benefit analysis')
legend(a)
legend('location','southeast')
legend('boxoff')
text(-0.1,1.1,'B','Units','normalized','FontWeight','bold','FontSize',16)

% Financial performance
subplot(4,1,3)
hold on
plot([n_years(1)-5 n_years(1)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
d = plot(n_years, GROSS_cumul_benefits,'LineWidth',1.5,...
    'DisplayName','Cumulative gross benefits',...
    'Color',[0 0.447058826684952 0.74117648601532]);
e = plot(n_years, NET_cumul_cashflow,'LineWidth',1.5,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078],...
    'DisplayName','Discounted cash flow');
f = plot(n_years, -NBS_cumul_investments,'LineWidth',1.5,...
    'Color',[0.929411768913269 0.694117665290833 0.125490203499794],...
    'DisplayName','Cumulative NBS investments');
bar(2020, NPV2080,...
    'FaceColor',[0.501960813999176 0.501960813999176 0.501960813999176],...
    'EdgeColor','none','BarWidth',0.5,...
    'DisplayName','Net present value (2021–2080)');
% Plot auxiliaries
plot([n_years(end) n_years(end)],[0 NPV2080],':','Color',[0 0 0])
plot([2020 n_years(end)],[NPV2080 NPV2080],':','Color',[0 0 0])
NPV2080str = ['NPV = ',num2str(round(NPV2080*100)/100)];
text(2021,.75*NPV2080,NPV2080str,'HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+1],'Ylim',[-55 105],'TickDir','out')
box off
% Labels
xlabel('Year')
ylabel('USD millions (NPV 2020, r = 3.46%)')
% title('Financial performance')
legend([d,f,e])
legend('location','northwest')
legend('boxoff')
text(-0.1,1.1,'C','Units','normalized','FontWeight','bold','FontSize',16)

% Plot ROI
subplot(4,1,4)
hold on
plot([n_years(1)-5 n_years(end)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
patch([n_years(:,1);n_years(end:-1:1)],[senbau_ROI;sendis_ROI(end:-1:1,end)],...
    [0.494117647409439 0.184313729405403 0.556862771511078],'Edgecolor','none','FaceAlpha',.25)
h = plot(n_years,ROI,'LineWidth',1.5,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078],...
    'DisplayName','Return on investment');
% Plot auxiliaries
plot([2020 2020],[-1 2.5],':','Color',[0 0 0])
plot([payback_plot payback_plot],[0 2.5],':','Color',[0 0 0])
plot([2020 payback_plot],[2.5 2.5],':','Color',[0 0 0],'Linewidth',1)
plot([payback_plot n_years(end)],[2.5 2.5],'Color',[0 0 0],'LineWidth',2)
text((payback_plot+2020)/2,2.65,'Payback',...
    'HorizontalAlignment','center')
text((n_years(end)+payback_plot)/2,2.65,'Profit',...
    'HorizontalAlignment','center')
text(n_years(end),sendis_ROI(end,end)+.1,[' r = ',num2str(100*sendis_r(end)),'%'],'HorizontalAlignment','left')
text(n_years(end),sendis_ROI(end,4)+.1,[' r = ',num2str(100*sendis_r(4)),'%'],'HorizontalAlignment','left')
text(n_years(end),senbau_ROI(end-2)+.1,' BAU x2','HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+1],'Ylim',[-1.1 2.6],'TickDir','out')
box off
% Labels
xlabel('Year')
% ylabel('ROI = (benefits – investments)/investments')
ylabel('Return on investment')
% title('Return on investment')
legend(h)
legend('location','southeast')
legend('boxoff')
legend('off')
text(-0.1,1.1,'D','Units','normalized','FontWeight','bold','FontSize',16)

% Export Figure
disp('Exporting the Figure to pdf')
% Set the paper size [width height]
set(ROI_Fig4alt,'PaperSize',[15 45]);
% set(ROI_Fig4alt,'PaperOrientation','landscape')
print(ROI_Fig4alt,'PNAS - ROI FONAG - Fig4alt','-dpdf','-fillpage')

disp('Finished plotting ROI Figure')
%% 11. Sensitivity analysis table
disp('11. Sensitivity analysis table')

% Table:     NPV2080            ROI2080             payback
table_ROI = [NPV2080            ROI2080             payback;...
             senbau_NPV2080     senbau_ROI2080      senbau_payback;...
             sennbs_NPV2080     sennbs_ROI2080      sennbs_payback;...
             senman_NPV2080     senman_ROI2080      senman_payback;...
             senwat_NPV2080     senwat_ROI2080      senwat_payback;...
             sendis_NPV2080(5)  sendis_ROI2080(5)   sendis_payback(5);...
             senddr_NPV2080     senddr_ROI2080      senddr_payback];

RESULTS_table = array2table(table_ROI,...
    'VariableNames',{'NPV2020','ROI','payback_year'},...
    'RowNames',{'original','BAU_2050','NBS_2040','NBS costs 1.5','water_tariff',...
    'r=9%','ddr:3.46%–0.5%'});
         
% Plot multiple ROI
ROI_FigS6 = figure;
set(ROI_FigS6,'Renderer','painters')
plot([n_years(1)-5 n_years(end)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
hold on
roi1 = plot(n_years,ROI,'LineWidth',2,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078],...
    'DisplayName','Original assumptions');
roi2 = plot(n_years,senbau_ROI,'LineWidth',1,...
    'DisplayName','Degradation peaks in 2050');
roi3 = plot(n_years,sennbs_ROI,'LineWidth',1,...
    'DisplayName','Full-size NBS effects peak in 2040');
roi4 = plot(n_years,senman_ROI,'LineWidth',1,...
    'DisplayName','NBS maintenance costs 50% more');
roi5 = plot(n_years,senwat_ROI,'LineWidth',1,...
    'DisplayName','Water tariff increases with inflation');
roi6 = plot(n_years,sendis_ROI(:,5),'LineWidth',1,...
    'DisplayName','Higher 9% discount rate');
roi7 = plot(n_years,senddr_ROI,'LineWidth',1,...
    'DisplayName','Declining discount rate');
roi8 = plot(n_years,sendis_ROI(:,2),'LineWidth',1,...
    'DisplayName','Zero 0% discount rate');
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+2],'Ylim',[-1.1 2.6],'TickDir','out')
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
set(ROI_FigS6,'PaperSize',[20 20]);
% set(ROI_FigS6,'PaperOrientation','landscape')
print(ROI_FigS6,'ROI_FigS6_export','-dpdf','-fillpage')

% Plot discount factors
ROI_FigS7 = figure;
set(ROI_FigS7,'Renderer','painters')
plot([n_years(1)-5 n_years(end)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
hold on
r1 = plot(n_years,NPV_factors(:,1),'LineWidth',1,...
    'DisplayName',[' r = ',num2str(100*sendis_r(1)),'%']);
r2 = plot(n_years,NPV_factors(:,2),'LineWidth',1,...
    'DisplayName',[' r = ',num2str(100*sendis_r(2)),'%']);
r3 = plot(n_years,NPV_factors(:,3),'LineWidth',1,...
    'DisplayName',[' r = ',num2str(100*sendis_r(3)),'%']);
r4 = plot(n_years,NPV_factors(:,4),'LineWidth',1,...
    'DisplayName',[' r = ',num2str(100*sendis_r(4)),'%']);
r5 = plot(n_years,NPV_factors(:,5),'LineWidth',1,...
    'DisplayName',[' r = ',num2str(100*sendis_r(5)),'%']);
ddr1 = plot(n_years,senddr_NPV_factors,'LineWidth',1,...
    'DisplayName','ddr = 3.46% (2021) – 0.5% (2080)');
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+2],'TickDir','out')
box off
% Labels
xlabel('Year')
ylabel('Discount factors')
% title('Discount factor')
legend([r1,r2,r3,r4,r5,ddr1])
legend('location','northwest')
legend('boxoff')

% Export Figure
disp('Exporting the Figure to pdf')
% Set the paper size [width height]
set(ROI_FigS7,'PaperSize',[20 20]);
% set(ROI_FigS7,'PaperOrientation','landscape')
print(ROI_FigS7,'ROI_FigS7_export','-dpdf','-fillpage')

disp('Finished sensitivity analysis table')
%% 12. Sensitivity analysis figure
disp('12. Sensitivity analysis figure')

% Plot
ROI_Fig5 = figure;
set(ROI_Fig5,'Renderer','painters')

% BAU scenario development
subplot(2,3,1)
hold on
plot([n_years(1)-5 n_years(end)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
patch([n_years(:,1);n_years(end:-1:1)],[senbau_ROI;senbau2_ROI(end:-1:1,end)],...
    [0.850980401039124 0.325490206480026 0.0980392172932625],...
    'Edgecolor','none','FaceAlpha',.25)
plot(n_years,ROI,'LineWidth',1.5,...
    'Color',[0.850980401039124 0.325490206480026 0.0980392172932625],...
    'DisplayName','Return on investment');
text(n_years(end),senbau_ROI(end)+.1,' BAU x2','HorizontalAlignment','left')
text(n_years(end),ROI(end),' BAU 2080','HorizontalAlignment','left')
text(n_years(end),senbau2_ROI(end)-.1,' BAU x1/2','HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+2],'Ylim',[-1.1 2.6],'TickDir','out')
box off
% Labels
xlabel('Year')
ylabel('Return on investment')
% title('Uncertainty in BAU scenario')
text(-0.1,1.1,'A','Units','normalized','FontWeight','bold','FontSize',16)

% NBS scenario development
subplot(2,3,2)
hold on
plot([n_years(1)-5 n_years(end)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
patch([n_years(:,1);n_years(end:-1:1)],[sennbs_ROI;sennbs2_ROI(end:-1:1,end)],...
    [0 0.498039215803146 0],...
    'Edgecolor','none','FaceAlpha',.25)
plot(n_years,ROI,'LineWidth',1.5,...
    'Color',[0 0.498039215803146 0],...
    'DisplayName','Return on investment');
text(n_years(end),sennbs_ROI(end)-.1,' NBS peak 2040','HorizontalAlignment','left')
text(n_years(end),ROI(end),' NBS peak 2030','HorizontalAlignment','left')
text(n_years(end),sennbs2_ROI(end)+.1,' NBS peak 2025','HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+2],'Ylim',[-1.1 2.6],'TickDir','out',...
    'YTickLabels',[])
box off
% Labels
xlabel('Year')
% ylabel('Return on investment')
% title('Uncertainty in NBS scenario')
text(-0.1,1.1,'B','Units','normalized','FontWeight','bold','FontSize',16)

% NBS maintenance costs
subplot(2,3,3)
hold on
plot([n_years(1)-5 n_years(end)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
patch([n_years(:,1);n_years(end:-1:1)],[senman_ROI;senman2_ROI(end:-1:1,end)],...
    [0.929411768913269 0.694117665290833 0.125490203499794],...
    'Edgecolor','none','FaceAlpha',.25)
plot(n_years,ROI,'LineWidth',1.5,...
    'Color',[0.929411768913269 0.694117665290833 0.125490203499794],...
    'DisplayName','Return on investment');
text(n_years(end),senman_ROI(end)-.1,' costs x2','HorizontalAlignment','left')
text(n_years(end),ROI(end),' NBS costs','HorizontalAlignment','left')
text(n_years(end),senman2_ROI(end)+.1,' costs x1/2','HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+2],'Ylim',[-1.1 2.6],'TickDir','out',...
    'YTickLabels',[])
box off
% Labels
xlabel('Year')
% ylabel('Return on investment')
% title('Uncertainty in NBS costs')
text(-0.1,1.1,'C','Units','normalized','FontWeight','bold','FontSize',16)

% Water tariff
subplot(2,3,4)
hold on
plot([n_years(1)-5 n_years(end)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
patch([n_years(:,1);n_years(end:-1:1)],[senwat_ROI;senwat2_ROI(end:-1:1,end)],...
    [0 0.447058826684952 0.74117648601532],...
    'Edgecolor','none','FaceAlpha',.25)
plot(n_years,ROI,'LineWidth',1.5,...
    'Color',[0 0.447058826684952 0.74117648601532],...
    'DisplayName','Return on investment');
text(n_years(end),senwat_ROI(end)+.1,' 1% inf.','HorizontalAlignment','left')
text(n_years(end),ROI(end),' 5%–5yr','HorizontalAlignment','left')
text(n_years(end),senwat2_ROI(end)+.05,' no increase ','HorizontalAlignment','left')
text(n_years(end),senwat2_ROI(end)-.1,' in water tariff','HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+2],'Ylim',[-1.1 2.6],'TickDir','out')
box off
% Labels
xlabel('Year')
ylabel('Return on investment')
% title('Uncertainty in water tariff increase')
text(-0.1,1.1,'D','Units','normalized','FontWeight','bold','FontSize',16)

% Discount rate
subplot(2,3,5)
hold on
plot([n_years(1)-5 n_years(end)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
patch([n_years(:,1);n_years(end:-1:1)],[sendis_ROI(:,2);sendis_ROI(end:-1:1,end)],...
    [0.1 0.1 0.1],...
    'Edgecolor','none','FaceAlpha',.25)
plot(n_years,ROI,'LineWidth',1.5,...
    'Color',[0.1 0.1 0.1],...
    'DisplayName','Return on investment');
plot(n_years,senddr_ROI,'LineWidth',1,'Color',[0.1 0.1 0.1],...
    'DisplayName','Return on investment');
text(n_years(end),sendis_ROI(end,2)+.1,[' r = ',num2str(100*sendis_r(2)),'%'],'HorizontalAlignment','left')
text(n_years(end),sendis_ROI(end,end)-.1,[' r = ',num2str(100*sendis_r(end)),'%'],'HorizontalAlignment','left')
text(n_years(end),ROI(end),[' r = ',num2str(100*sendis_r(4)),'%'],'HorizontalAlignment','left')
text(n_years(end),senddr_ROI(end),' DDR to 0.5%','HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+2],'Ylim',[-1.1 2.6],'TickDir','out',...
    'YTickLabels',[])
box off
% Labels
xlabel('Year')
% ylabel('Return on investment')
% title('Uncertainty in discount rate')
text(-0.1,1.1,'E','Units','normalized','FontWeight','bold','FontSize',16)

% ROI combined uncertainty
subplot(2,3,6)
hold on
plot([n_years(1)-5 n_years(end)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
% patch([n_years(:,1);n_years(end:-1:1)],[senbau_ROI;sendis_ROI(end:-1:1,end)],...
%     [0.494117647409439 0.184313729405403 0.556862771511078],'Edgecolor','none','FaceAlpha',.25)
patch([n_years(:,1);n_years(end:-1:1)],[senbau_ROI;senbau2_ROI(end:-1:1,end)],...
    [0.494117647409439 0.184313729405403 0.556862771511078],...
    'Edgecolor','none','FaceAlpha',.25)
patch([n_years(:,1);n_years(end:-1:1)],[sennbs_ROI;sennbs2_ROI(end:-1:1,end)],...
    [0.494117647409439 0.184313729405403 0.556862771511078],...
    'Edgecolor','none','FaceAlpha',.25)
patch([n_years(:,1);n_years(end:-1:1)],[senman_ROI;senman2_ROI(end:-1:1,end)],...
    [0.494117647409439 0.184313729405403 0.556862771511078],...
    'Edgecolor','none','FaceAlpha',.25)
patch([n_years(:,1);n_years(end:-1:1)],[senwat_ROI;senwat2_ROI(end:-1:1,end)],...
    [0.494117647409439 0.184313729405403 0.556862771511078],...
    'Edgecolor','none','FaceAlpha',.25)
patch([n_years(:,1);n_years(end:-1:1)],[sendis_ROI(:,2);sendis_ROI(end:-1:1,end)],...
    [0.494117647409439 0.184313729405403 0.556862771511078],...
    'Edgecolor','none','FaceAlpha',.25)
plot(n_years,ROI,'LineWidth',1.5,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078],...
    'DisplayName','Return on investment');
% Plot auxiliaries
plot([2020 2020],[-1 2.5],':','Color',[0 0 0])
plot([payback_plot payback_plot],[0 2.5],':','Color',[0 0 0])
plot([2020 payback_plot],[2.5 2.5],':','Color',[0 0 0],'Linewidth',1)
plot([payback_plot n_years(end)],[2.5 2.5],'Color',[0 0 0],'LineWidth',2)
text((payback_plot+2020)/2,2.65,'Payback',...
    'HorizontalAlignment','center')
text((n_years(end)+payback_plot)/2,2.65,'Profit',...
    'HorizontalAlignment','center')
text(n_years(end),sendis_ROI(end,end)-.1,[' r = ',num2str(100*sendis_r(end)),'%'],'HorizontalAlignment','left')
text(n_years(end),ROI(end),[' r = ',num2str(100*sendis_r(4)),'%'],'HorizontalAlignment','left')
text(n_years(end),senbau_ROI(end)+.1,' BAU x2','HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+2],'Ylim',[-1.1 2.6],'TickDir','out',...
    'YTickLabels',[])
box off
% Labels
xlabel('Year')
% ylabel('Return on investment')
% title('Combined results')
text(-0.1,1.1,'F','Units','normalized','FontWeight','bold','FontSize',16)

% Export Figure
disp('Exporting the Figure to pdf')
% Set the paper size [width height]
set(ROI_Fig5,'PaperSize',[40 25]);
% set(ROI_Fig5,'PaperOrientation','landscape')
print(ROI_Fig5,'PNAS - ROI FONAG - Fig5','-dpdf','-fillpage')

% ALTERNATIVE FIGURE
% Plot
ROI_Fig5alt = figure;
set(ROI_Fig5alt,'Renderer','painters')

hold on
plot([n_years(1)-5 n_years(end)+5],[0 0],'Color',[0.25 0.25 0.25],'LineWidth',1)
patch([n_years(:,1);n_years(end:-1:1)],[senbau_ROI;senbau2_ROI(end:-1:1,end)],...
    [0.850980401039124 0.325490206480026 0.0980392172932625],...
    'Edgecolor','none','FaceAlpha',.25)
patch([n_years(:,1);n_years(end:-1:1)],[sennbs_ROI;sennbs2_ROI(end:-1:1,end)],...
    [0 0.498039215803146 0],...
    'Edgecolor','none','FaceAlpha',.25)
patch([n_years(:,1);n_years(end:-1:1)],[senman_ROI;senman2_ROI(end:-1:1,end)],...
    [0.929411768913269 0.694117665290833 0.125490203499794],'Edgecolor','none','FaceAlpha',.25)
patch([n_years(:,1);n_years(end:-1:1)],[senwat_ROI;senwat2_ROI(end:-1:1,end)],...
    [0 0.447058826684952 0.74117648601532],...
    'Edgecolor','none','FaceAlpha',.25)
patch([n_years(:,1);n_years(end:-1:1)],[sendis_ROI(:,2);sendis_ROI(end:-1:1,end)],...
    [0.1 0.1 0.1],'Edgecolor','none','FaceAlpha',.25)
plot(n_years,senddr_ROI,'LineWidth',1,'Color',[0.25 0.25 0.25],...
    'DisplayName','Return on investment');
plot(n_years,ROI,'LineWidth',1.5,...
    'Color',[0.494117647409439 0.184313729405403 0.556862771511078],...
    'DisplayName','Return on investment');
% Plot auxiliaries
plot([2020 2020],[-1 2.5],':','Color',[0 0 0])
plot([payback_plot payback_plot],[0 2.5],':','Color',[0 0 0])
plot([2020 payback_plot],[2.5 2.5],':','Color',[0 0 0],'Linewidth',1)
plot([payback_plot n_years(end)],[2.5 2.5],'Color',[0 0 0],'LineWidth',2)
text((payback_plot+2020)/2,2.6,'Payback','HorizontalAlignment','center')
text((n_years(end)+payback_plot)/2,2.6,'Profit','HorizontalAlignment','center')
% Labels
text(n_years(end),senbau_ROI(end),' BAU rate x2','HorizontalAlignment','left')
text(n_years(end),senbau2_ROI(end)+.05,' BAU rate x1/2','HorizontalAlignment','left')
text(n_years(end),sennbs_ROI(end),' NBS peak 2040','HorizontalAlignment','left')
text(n_years(end),sennbs2_ROI(end)+.1,' NBS peak 2025','HorizontalAlignment','left')
text(n_years(end),senman_ROI(end),' NBS costs x2','HorizontalAlignment','left')
text(n_years(end),senman2_ROI(end),' NBS costs x1/2','HorizontalAlignment','left')
text(n_years(end),senwat_ROI(end)-.05,' 1% inf. tariff','HorizontalAlignment','left')
text(n_years(end),senwat2_ROI(end),' no tariff increase','HorizontalAlignment','left')
text(n_years(end),sendis_ROI(end,2),[' r = ',num2str(100*sendis_r(2)),'%'],'HorizontalAlignment','left')
text(n_years(end),sendis_ROI(end,end),[' r = ',num2str(100*sendis_r(end)),'%'],'HorizontalAlignment','left')
text(n_years(end),senddr_ROI(end),' DDR to 0.5%','HorizontalAlignment','left')
text(n_years(end),ROI(end),' Original assumptions','HorizontalAlignment','left')
% Plot settings
set(gca,'Xlim',[n_years(1) n_years(end)+5],'Ylim',[-1.1 2.6],'TickDir','out')
box off
% Labels
xlabel('Year')
ylabel('Return on investment')

% Export Figure
disp('Exporting the Figure to pdf')
% Set the paper size [width height]
set(ROI_Fig5alt,'PaperSize',[20 20]);
% set(ROI_Fig5alt,'PaperOrientation','landscape')
print(ROI_Fig5alt,'PNAS - ROI FONAG - Fig5alt','-dpdf','-fillpage')

disp('Finished saving results')
%% 13. Save results
disp('13. Saving results')

RESULTS = array2table([n_years,BAU_yearly_losses,NBS_yearly_benefits,...
    GROSS_yearly_benefits,NBS_yearly_investments,NET_yearly_cashflow,...
    BAU_cumul_losses,NBS_cumul_benefits,GROSS_cumul_benefits,...
    NBS_cumul_investments,NET_cumul_cashflow,ROI],...
    'VariableNames',{'years','BAU_yearly_losses','NBS_yearly_benefits',...
    'GROSS_yearly_benefits','NBS_yearly_investments','NET_yearly_cashflow',...
    'BAU_cumul_losses','NBS_cumul_benefits','GROSS_cumul_benefits',...
    'NBS_cumul_investments','NET_cumul_cashflow','ROI'});

RESULTS_NORATE = array2table([n_years,norate_BAU_yearly_losses,norate_NBS_yearly_benefits,...
    norate_GROSS_yearly_benefits,norate_NBS_yearly_investments,norate_NET_yearly_cashflow,...
    norate_BAU_cumul_losses,norate_NBS_cumul_benefits,norate_GROSS_cumul_benefits,...
    norate_NBS_cumul_investments,norate_NET_cumul_cashflow],...
    'VariableNAmes',{'years','norate_BAU_yearly_losses','norate_NBS_yearly_benefits',...
    'norate_GROSS_yearly_benefits','norate_NBS_yearly_investments','norate_NET_yearly_cashflow',...
    'norate_BAU_cumul_losses','norate_NBS_cumul_benefits','norate_GROSS_cumul_benefits',...
    'norate_NBS_cumul_investments','norate_NET_cumul_cashflow'});

RESULTS_NPV_FACTORS = array2table([1./NPV_factors,1./senddr_NPV_factors],...
    'VariableNAmes',{'-1%','0%','1%','3.46%','9%','ddr=3.46%–0.5%'});

RESULTS_sensitivity_BAU2050 = array2table([n_years,senbau_BAU_yearly_losses,NBS_yearly_benefits,...
    senbau_GROSS_yearly_benefits,NBS_yearly_investments,senbau_NET_yearly_cashflow,...
    senbau_BAU_cumul_losses,NBS_cumul_benefits,senbau_GROSS_cumul_benefits,...
    NBS_cumul_investments,senbau_NET_cumul_cashflow,senbau_ROI],...
    'VariableNames',{'years','senbau_BAU_yearly_losses','NBS_yearly_benefits',...
    'senbau_GROSS_yearly_benefits','NBS_yearly_investments','senbau_NET_yearly_cashflow',...
    'senbau_BAU_cumul_losses','NBS_cumul_benefits','senbau_GROSS_cumul_benefits',...
    'NBS_cumul_investments','senbau_NET_cumul_cashflow','senbau_ROI'});

RESULTS_sensitivity_NBS2040 = array2table([n_years,BAU_yearly_losses,sennbs_NBS_yearly_benefits,...
    sennbs_GROSS_yearly_benefits,NBS_yearly_investments,sennbs_NET_yearly_cashflow,...
    BAU_cumul_losses,sennbs_NBS_cumul_benefits,sennbs_GROSS_cumul_benefits,...
    NBS_cumul_investments,sennbs_NET_cumul_cashflow,sennbs_ROI],...
    'VariableNames',{'years','BAU_yearly_losses','sennbs_NBS_yearly_benefits',...
    'sennbs_GROSS_yearly_benefits','NBS_yearly_investments','sennbs_NET_yearly_cashflow',...
    'BAU_cumul_losses','sennbs_NBS_cumul_benefits','sennbs_GROSS_cumul_benefits',...
    'NBS_cumul_investments','sennbs_NET_cumul_cashflow','sennbs_ROI'});

RESULTS_sensitivity_NBS_costs = array2table([n_years,BAU_yearly_losses,NBS_yearly_benefits,...
    GROSS_yearly_benefits,senman_NBS_yearly_investments,senman_NET_yearly_cashflow,...
    BAU_cumul_losses,NBS_cumul_benefits,GROSS_cumul_benefits,...
    senman_NBS_cumul_investments,senman_NET_cumul_cashflow,senman_ROI],...
    'VariableNames',{'years','BAU_yearly_losses','NBS_yearly_benefits',...
    'GROSS_yearly_benefits','senman_NBS_yearly_investments','senman_NET_yearly_cashflow',...
    'BAU_cumul_losses','NBS_cumul_benefits','GROSS_cumul_benefits',...
    'senman_NBS_cumul_investments','senman_NET_cumul_cashflow','senman_ROI'});

RESULTS_sensitivity_TARIFF = array2table([n_years,senwat_BAU_yearly_losses,senwat_NBS_yearly_benefits,...
    senwat_GROSS_yearly_benefits,NBS_yearly_investments,senwat_NET_yearly_cashflow,...
    senwat_BAU_cumul_losses,senwat_NBS_cumul_benefits,senwat_GROSS_cumul_benefits,...
    NBS_cumul_investments,senwat_NET_cumul_cashflow,senwat_ROI],...
    'VariableNames',{'years','senwat_BAU_yearly_losses','senwat_NBS_yearly_benefits',...
    'senwat_GROSS_yearly_benefits','NBS_yearly_investments','senwat_NET_yearly_cashflow',...
    'senwat_BAU_cumul_losses','senwat_NBS_cumul_benefits','senwat_GROSS_cumul_benefits',...
    'NBS_cumul_investments','senwat_NET_cumul_cashflow','senwat_ROI'});

RESULTS_sensitivity_dr9 = array2table([n_years,sendis_BAU_yearly_losses(:,end),sendis_NBS_yearly_benefits(:,end),...
    sendis_GROSS_yearly_benefits(:,end),sendis_NBS_yearly_investments(:,end),sendis_NET_yearly_cashflow(:,end),...
    sendis_BAU_cumul_losses(:,end),sendis_NBS_cumul_benefits(:,end),sendis_GROSS_cumul_benefits(:,end),...
    sendis_NBS_cumul_investments(:,end),sendis_NET_cumul_cashflow(:,end),sendis_ROI(:,end)],...
    'VariableNames',{'years','sendr9_BAU_yearly_losses','sendr9_NBS_yearly_benefits',...
    'sendr9_GROSS_yearly_benefits','sendr9_NBS_yearly_investments','sendr9_NET_yearly_cashflow',...
    'sendr9_BAU_cumul_losses','sendr9_NBS_cumul_benefits','sendr9_GROSS_cumul_benefits',...
    'sendr9_NBS_cumul_investments','sendr9_NET_cumul_cashflow','sendr9_ROI'});

RESULTS_sensitivity_ddr = array2table([n_years,senddr_BAU_yearly_losses,senddr_NBS_yearly_benefits,...
    senddr_GROSS_yearly_benefits,senddr_NBS_yearly_investments,senddr_NET_yearly_cashflow,...
    senddr_BAU_cumul_losses,senddr_NBS_cumul_benefits,senddr_GROSS_cumul_benefits,...
    senddr_NBS_cumul_investments,senddr_NET_cumul_cashflow,senddr_ROI],...
    'VariableNames',{'years','senddr_BAU_yearly_losses','senddr_NBS_yearly_benefits',...
    'senddr_GROSS_yearly_benefits','senddr_NBS_yearly_investments','senddr_NET_yearly_cashflow',...
    'senddr_BAU_cumul_losses','senddr_NBS_cumul_benefits','senddr_GROSS_cumul_benefits',...
    'senddr_NBS_cumul_investments','senddr_NET_cumul_cashflow','senddr_ROI'});

writetable(RESULTS_table,'RESULTS_table.csv','Delimiter',',')
writetable(RESULTS,'RESULTS.csv','Delimiter',',')
writetable(RESULTS_NORATE,'RESULTS_NORATE.csv','Delimiter',',')
writetable(RESULTS_NPV_FACTORS,'RESULTS_NPV_FACTORS.csv','Delimiter',',')
writetable(RESULTS_sensitivity_BAU2050,'RESULTS_sensitivity_BAU2050.csv','Delimiter',',')
writetable(RESULTS_sensitivity_NBS2040,'RESULTS_sensitivity_NBS2040.csv','Delimiter',',')
writetable(RESULTS_sensitivity_NBS_costs,'RESULTS_sensitivity_NBS_costs.csv','Delimiter',',')
writetable(RESULTS_sensitivity_TARIFF,'RESULTS_sensitivity_TARIFF.csv','Delimiter',',')
writetable(RESULTS_sensitivity_dr9,'RESULTS_sensitivity_dr9.csv','Delimiter',',')
writetable(RESULTS_sensitivity_ddr,'RESULTS_sensitivity_ddr.csv','Delimiter',',')

clear a b c d e f g h i l m n n_pos NPV2080str
clear roi1 roi2 roi3 roi4 roi5 roi6 roi7 roi8 sendis_find
clear r1 r2 r3 r4 r5 ddr1
clear ROI_Fig4 ROI_Fig5 ROI_FigS6 ROI_FigS7 ROI_Fig4alt ROI_Fig5alt

save ROI_FONAG

disp('Finished saving results') 