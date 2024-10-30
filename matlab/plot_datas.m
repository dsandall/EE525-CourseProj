files = dir('../sensors_data*.csv'); 

% Initialize an array to store the datetime values
timestamps = NaT(length(files), 1);  % NaT = Not-a-Time, default value for datetime array

% Loop through the files and extract date and time
for i = 1:length(files)
    % Extract date and time portion from the filename (assumes the format is correct)
    tokens = regexp(files(i).name, 'sensors_data_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2}).*', 'tokens');
    
    if ~isempty(tokens)
        % Convert to datetime, replacing hyphens with colons for the time part
        dateStr = tokens{1}{1};  % 'YYYY-MM-DD'
        timeStr = strrep(tokens{1}{2}, '-', ':');  % 'HH:MM:SS'
        timestamps(i) = datetime([dateStr ' ' timeStr], 'InputFormat', 'yyyy-MM-dd HH:mm:ss');
    end
end

% Find the most recent timestamp
[~, mostRecentIdx] = max(timestamps);

% Get the filename of the most recent file
mostRecentFile = files(mostRecentIdx).name;

% Display the most recent file
disp(['Most recent file: ', mostRecentFile]);

% Full path to the most recent file
mostRecentFilePath = fullfile(files(mostRecentIdx).folder, mostRecentFile);

% Adjust for new variable names
time = data.("Time (s)");
accelX1 = data.("Accel X1");
accelY1 = data.("Accel Y1");
accelZ1 = data.("Accel Z1");
accelX2 = data.("Accel X2");
accelY2 = data.("Accel Y2");
accelZ2_unfiltered = data.("Accel Z2");

accelZ2 = filloutliers(accelZ2_unfiltered, 'linear', 'movmedian', 2);



% Compute the sample intervals (time differences between consecutive samples)
timeDiffs = diff(time);  % Time differences between consecutive samples

% Calculate sample frequency
sampleFrequency = 1 ./ mean(timeDiffs);  % Inverse of the mean time difference

% Calculate precision metrics (standard deviation of time intervals)
sampleStdDev = std(timeDiffs);

% Display metrics in the terminal
fprintf('Sample frequency: %.2f Hz\n', sampleFrequency);
fprintf('Average time interval: %.6f seconds\n', mean(timeDiffs));
fprintf('Time interval standard deviation: %.6f seconds\n', sampleStdDev);
% Calculate integrals for acceleration to get velocity and displacement (for both sensors)
velocityZ1 = cumtrapz(time, accelZ1);
distZ1 = cumtrapz(time, velocityZ1);

velocityZ2 = cumtrapz(time, accelZ2);
distZ2 = cumtrapz(time, velocityZ2);

% Plotting

MAX_SAMPLE_T = 4.4;

% Acceleration Z for both sensors
figure;
plot(time, accelZ1, 'b', 'DisplayName', 'MPU6050 Accel Z');
hold on;
plot(time, accelZ2, 'r', 'DisplayName', 'ADXL345 Accel Z');
xlabel('Time (s)');
ylabel('Acceleration Z (m/s^2)');
title('Acceleration Z over Time for MPU6050 and ADXL345');
legend;
xlim([0 MAX_SAMPLE_T]);
ylim([-2.5 2.5]);

% Velocity Z for both sensors
figure;
plot(time, velocityZ1, 'b', 'DisplayName', 'MPU6050 Velocity Z');
hold on;
plot(time, velocityZ2, 'r', 'DisplayName', 'ADXL345 Velocity Z');
xlabel('Time (s)');
ylabel('Velocity Z (m/s)');
title('Velocity Z over Time for MPU6050 and ADXL345');
legend;
xlim([0 MAX_SAMPLE_T]);
ylim([-0.6 0.6]);

% Compute detrended Accel Z for both sensors
firstIndex = find(time <= 0.2, 1, 'last');
medAccelZ1 = median(accelZ1(1:firstIndex));
medAccelZ2 = median(accelZ2(1:firstIndex));

accelZ1_detrended = accelZ1 - medAccelZ1;
accelZ2_detrended = accelZ2 - medAccelZ2;

% truncate ridiculous vals
accelZ1_detrended = max(-2, min(accelZ1_detrended, 2));
accelZ2_detrended = max(-2, min(accelZ2_detrended, 2));

fprintf('Mean of MPU6050 Accel Z during first 0.2 seconds: %.4f m/s^2\n', medAccelZ1);
fprintf('Mean of ADXL345 Accel Z during first 0.2 seconds: %.4f m/s^2\n', medAccelZ2);


% Detrended Acceleration Z
figure;
plot(time, accelZ1_detrended, 'b', 'DisplayName', 'MPU6050 Detrended Accel Z');
hold on;
plot(time, accelZ2_detrended, 'r', 'DisplayName', 'ADXL345 Detrended Accel Z');
xlabel('Time (s)');
ylabel('Detrended Acceleration Z (m/s^2)');
title('Detrended Acceleration Z over Time for MPU6050 and ADXL345');
legend;
xlim([0 MAX_SAMPLE_T]);
ylim([-2.5 2.5]);

% Detrended Velocity Z
velocityZ1_detrended = cumtrapz(time, accelZ1_detrended);
velocityZ2_detrended = cumtrapz(time, accelZ2_detrended);

figure;
plot(time, velocityZ1_detrended, 'b', 'DisplayName', 'MPU6050 Detrended Velocity Z');
hold on;
plot(time, velocityZ2_detrended, 'r', 'DisplayName', 'ADXL345 Detrended Velocity Z');
xlabel('Time (s)');
ylabel('Velocity Z (m/s)');
title('Detrended Velocity Z over Time for MPU6050 and ADXL345');
legend;
xlim([0 MAX_SAMPLE_T]);
ylim([-0.6 0.6]);
