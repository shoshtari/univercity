script_path = mfilename('fullpath');
project_root = fileparts(fileparts(script_path));
dataset_root = fullfile(project_root, 'data', 'dataset', 'benchmarks');
dataset_names = {'BSDS100', 'urban100', 'manga109'};
scales = [2, 3, 4];

for dataset_index = 1:numel(dataset_names)
    source_dir = fullfile(dataset_root, dataset_names{dataset_index});
    images = dir(fullfile(source_dir, '*.png'));
    if isempty(images)
        error('No PNG images were found in %s', source_dir);
    end
    for scale = scales
        output_dir = fullfile(source_dir, sprintf('LRbicx%d', scale));
        if ~exist(output_dir, 'dir')
            mkdir(output_dir);
        end
        for image_index = 1:numel(images)
            source_path = fullfile(source_dir, images(image_index).name);
            output_path = fullfile(output_dir, images(image_index).name);
            if exist(output_path, 'file')
                continue;
            end
            high_resolution = imread(source_path);
            height = floor(size(high_resolution, 1) / scale) * scale;
            width = floor(size(high_resolution, 2) / scale) * scale;
            high_resolution = high_resolution(1:height, 1:width, :);
            low_resolution = imresize(high_resolution, 1 / scale, 'bicubic', ...
                'Antialiasing', true);
            imwrite(low_resolution, output_path);
        end
        fprintf('%s x%d: %d images ready.\n', dataset_names{dataset_index}, ...
            scale, numel(images));
    end
end
