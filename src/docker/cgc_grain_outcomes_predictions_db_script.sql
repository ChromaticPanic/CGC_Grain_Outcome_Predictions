create table ab_hly_station_data
(
    id                  serial
        constraint pk_ab_hly_station_data
            primary key,
    station_id          varchar,
    year                integer,
    month               integer,
    day                 integer,
    min_temp            double precision,
    max_temp            double precision,
    mean_temp           double precision,
    min_dew_point_temp  double precision,
    max_dew_point_temp  double precision,
    mean_dew_point_temp double precision,
    min_humidex         double precision,
    max_humidex         double precision,
    mean_humidex        double precision,
    total_precip        double precision,
    min_rel_humid       double precision,
    max_rel_humid       double precision,
    mean_rel_humid      double precision,
    min_stn_press       double precision,
    max_stn_press       double precision,
    mean_stn_press      double precision,
    min_visibility      double precision,
    max_visibility      double precision,
    mean_visibility     double precision
);

alter table ab_hly_station_data
    owner to postgres;


create table ab_station_data
(
    station_id   text,
    date         timestamp,
    year         bigint,
    month        bigint,
    day          bigint,
    max_temp     double precision,
    min_temp     double precision,
    mean_temp    double precision,
    total_rain   double precision,
    total_snow   double precision,
    total_precip double precision,
    snow_on_grnd double precision
);

alter table ab_station_data
    owner to postgres;

create table agg_day_copernicus_satellite_data
(
    year                                 bigint,
    month                                bigint,
    day                                  bigint,
    cr_num                               bigint,
    district                             bigint,
    min_dewpoint_temperature             double precision,
    max_dewpoint_temperature             double precision,
    mean_dewpoint_temperature            double precision,
    min_temperature                      double precision,
    max_temperature                      double precision,
    mean_temperature                     double precision,
    min_evaporation_from_bare_soil       double precision,
    max_evaporation_from_bare_soil       double precision,
    mean_evaporation_from_bare_soil      double precision,
    min_skin_reservoir_content           double precision,
    max_skin_reservoir_content           double precision,
    mean_skin_reservoir_content          double precision,
    min_skin_temperature                 double precision,
    max_skin_temperature                 double precision,
    mean_skin_temperature                double precision,
    min_snowmelt                         double precision,
    max_snowmelt                         double precision,
    mean_snowmelt                        double precision,
    min_soil_temperature_level_1         double precision,
    max_soil_temperature_level_1         double precision,
    mean_soil_temperature_level_1        double precision,
    min_soil_temperature_level_2         double precision,
    max_soil_temperature_level_2         double precision,
    mean_soil_temperature_level_2        double precision,
    min_soil_temperature_level_3         double precision,
    max_soil_temperature_level_3         double precision,
    mean_soil_temperature_level_3        double precision,
    min_soil_temperature_level_4         double precision,
    max_soil_temperature_level_4         double precision,
    mean_soil_temperature_level_4        double precision,
    min_surface_net_solar_radiation      double precision,
    max_surface_net_solar_radiation      double precision,
    mean_surface_net_solar_radiation     double precision,
    min_surface_pressure                 double precision,
    max_surface_pressure                 double precision,
    mean_surface_pressure                double precision,
    min_volumetric_soil_water_layer_1    double precision,
    max_volumetric_soil_water_layer_1    double precision,
    mean_volumetric_soil_water_layer_1   double precision,
    min_volumetric_soil_water_layer_2    double precision,
    max_volumetric_soil_water_layer_2    double precision,
    mean_volumetric_soil_water_layer_2   double precision,
    min_volumetric_soil_water_layer_3    double precision,
    max_volumetric_soil_water_layer_3    double precision,
    mean_volumetric_soil_water_layer_3   double precision,
    min_volumetric_soil_water_layer_4    double precision,
    max_volumetric_soil_water_layer_4    double precision,
    mean_volumetric_soil_water_layer_4   double precision,
    min_leaf_area_index_high_vegetation  double precision,
    max_leaf_area_index_high_vegetation  double precision,
    mean_leaf_area_index_high_vegetation double precision,
    min_leaf_area_index_low_vegetation   double precision,
    max_leaf_area_index_low_vegetation   double precision,
    mean_leaf_area_index_low_vegetation  double precision
);

alter table agg_day_copernicus_satellite_data
    owner to postgres;

create table agg_ergot_samples
(
    sample_id            bigint,
    year                 bigint,
    province             text,
    crop_district        bigint,
    incidence            boolean,
    severity             double precision,
    district             integer,
    percnt_true          double precision,
    has_ergot            boolean,
    sum_severity         double precision,
    present_prev1        boolean,
    present_prev2        boolean,
    present_prev3        boolean,
    present_in_neighbor  boolean,
    severity_prev1       double precision,
    severity_prev2       double precision,
    severity_prev3       double precision,
    severity_in_neighbor double precision
);

alter table agg_ergot_samples
    owner to postgres;

create table agg_soil_data
(
    poly_id                         bigint,
    cmp                             bigint,
    percent                         bigint,
    province                        text,
    soil_id                         text,
    water_holding_cap               double precision,
    name                            text,
    percnt_coarse_frag              bigint,
    total_sand                      bigint,
    total_silt                      bigint,
    total_clay                      bigint,
    percnt_carbon                   double precision,
    calcium_ph                      double precision,
    proj_ph                         double precision,
    water_reten_0                   bigint,
    water_reten_10                  bigint,
    water_reten_33                  bigint,
    water_reten_1500                bigint,
    bulk_density                    double precision,
    elec_cond                       bigint,
    percnt_wood                     bigint,
    land_area                       bigint,
    water_area                      bigint,
    area                            double precision,
    perimeter                       double precision,
    district                        bigint,
    "profile_A"                     boolean,
    "profile_N"                     boolean,
    "kind_M"                        boolean,
    "kind_N"                        boolean,
    "kind_O"                        boolean,
    "kind_U"                        boolean,
    "water_table_-"                 boolean,
    "water_table_NO"                boolean,
    "water_table_YB"                boolean,
    "water_table_YG"                boolean,
    "water_table_YU"                boolean,
    "root_restrict_-"               boolean,
    root_restrict_0                 boolean,
    root_restrict_1                 boolean,
    root_restrict_2                 boolean,
    root_restrict_3                 boolean,
    root_restrict_4                 boolean,
    root_restrict_5                 boolean,
    root_restrict_6                 boolean,
    root_restrict_7                 boolean,
    root_restrict_8                 boolean,
    root_restrict_9                 boolean,
    "drainage_-"                    boolean,
    "drainage_I"                    boolean,
    "drainage_MW"                   boolean,
    "drainage_P"                    boolean,
    "drainage_R"                    boolean,
    "drainage_VP"                   boolean,
    "drainage_VR"                   boolean,
    "drainage_W"                    boolean,
    "parent_material_texture_1_-"   boolean,
    "parent_material_texture_1_C"   boolean,
    "parent_material_texture_1_CS"  boolean,
    "parent_material_texture_1_F"   boolean,
    "parent_material_texture_1_FI"  boolean,
    "parent_material_texture_1_HU"  boolean,
    "parent_material_texture_1_M"   boolean,
    "parent_material_texture_1_MC"  boolean,
    "parent_material_texture_1_ME"  boolean,
    "parent_material_texture_1_MF"  boolean,
    "parent_material_texture_1_UD"  boolean,
    "parent_material_texture_1_VC"  boolean,
    "parent_material_texture_1_VF"  boolean,
    "parent_material_chemical_1_-"  boolean,
    "parent_material_chemical_1_AN" boolean,
    "parent_material_chemical_1_EA" boolean,
    "parent_material_chemical_1_EC" boolean,
    "parent_material_chemical_1_SA" boolean,
    "parent_material_chemical_1_UD" boolean,
    "parent_material_chemical_1_VC" boolean,
    "parent_material_chemical_1_WC" boolean,
    "mode_of_depo_1_-"              boolean,
    "mode_of_depo_1_COLL"           boolean,
    "mode_of_depo_1_EOLI"           boolean,
    "mode_of_depo_1_FLEO"           boolean,
    "mode_of_depo_1_FLLC"           boolean,
    "mode_of_depo_1_FLUV"           boolean,
    "mode_of_depo_1_FNPT"           boolean,
    "mode_of_depo_1_FOPT"           boolean,
    "mode_of_depo_1_GLFL"           boolean,
    "mode_of_depo_1_GLLC"           boolean,
    "mode_of_depo_1_LACU"           boolean,
    "mode_of_depo_1_LATL"           boolean,
    "mode_of_depo_1_RESD"           boolean,
    "mode_of_depo_1_RKIA"           boolean,
    "mode_of_depo_1_RKLS"           boolean,
    "mode_of_depo_1_RKUD"           boolean,
    "mode_of_depo_1_SPPT"           boolean,
    "mode_of_depo_1_TILL"           boolean,
    "mode_of_depo_1_UNDM"           boolean,
    "sand_texture_-"                boolean,
    "sand_texture_C"                boolean,
    "sand_texture_F"                boolean,
    "sand_texture_M"                boolean,
    "sand_texture_VC"               boolean,
    "sand_texture_VF"               boolean
);

alter table agg_soil_data
    owner to postgres;

create table agg_soil_moisture
(
    index              bigint,
    year               integer,
    month              integer,
    day                integer,
    cr_num             bigint,
    district           bigint,
    soil_moisture_min  double precision,
    soil_moisture_max  double precision,
    soil_moisture_mean double precision
);

alter table agg_soil_moisture
    owner to postgres;

create index ix_public_agg_soil_moisture_index
    on agg_soil_moisture (index);



create table census_ag_regions
(
    district bigint,
    car_name text,
    pr_uid   bigint,
    ag_uid   text,
    geometry geometry(Geometry, 3347),
    color    text,
    cr_num   bigint
);

alter table census_ag_regions
    owner to postgres;

create index idx_census_ag_regions_geometry
    on census_ag_regions using gist (geometry);

create table ergot_sample
(
    sample_id     serial
        constraint pk_ergot_sample
            primary key,
    year          integer,
    province      varchar,
    crop_district integer,
    incidence     boolean,
    severity      double precision
);

alter table ergot_sample
    owner to postgres;

create table labeled_soil
(
    id       bigint,
    poly_id  bigint,
    soil_ids text,
    cr_num   double precision,
    district integer
);

alter table labeled_soil
    owner to postgres;

create table mb_hly_station_data
(
    id                  serial
        constraint pk_mb_hly_station_data
            primary key,
    station_id          varchar,
    year                integer,
    month               integer,
    day                 integer,
    min_temp            double precision,
    max_temp            double precision,
    mean_temp           double precision,
    min_dew_point_temp  double precision,
    max_dew_point_temp  double precision,
    mean_dew_point_temp double precision,
    min_humidex         double precision,
    max_humidex         double precision,
    mean_humidex        double precision,
    total_precip        double precision,
    min_rel_humid       double precision,
    max_rel_humid       double precision,
    mean_rel_humid      double precision,
    min_stn_press       double precision,
    max_stn_press       double precision,
    mean_stn_press      double precision,
    min_visibility      double precision,
    max_visibility      double precision,
    mean_visibility     double precision
);

alter table mb_hly_station_data
    owner to postgres;

create table mb_station_data
(
    station_id   text,
    date         timestamp,
    year         bigint,
    month        bigint,
    day          bigint,
    max_temp     double precision,
    min_temp     double precision,
    mean_temp    double precision,
    total_rain   double precision,
    total_snow   double precision,
    total_precip double precision,
    snow_on_grnd double precision
);

alter table mb_station_data
    owner to postgres;

create table sk_hly_station_data
(
    id                  serial
        constraint pk_sk_hly_station_data
            primary key,
    station_id          varchar,
    year                integer,
    month               integer,
    day                 integer,
    min_temp            double precision,
    max_temp            double precision,
    mean_temp           double precision,
    min_dew_point_temp  double precision,
    max_dew_point_temp  double precision,
    mean_dew_point_temp double precision,
    min_humidex         double precision,
    max_humidex         double precision,
    mean_humidex        double precision,
    total_precip        double precision,
    min_rel_humid       double precision,
    max_rel_humid       double precision,
    mean_rel_humid      double precision,
    min_stn_press       double precision,
    max_stn_press       double precision,
    mean_stn_press      double precision,
    min_visibility      double precision,
    max_visibility      double precision,
    mean_visibility     double precision
);

alter table sk_hly_station_data
    owner to postgres;

create table sk_station_data
(
    station_id   text,
    date         timestamp,
    year         bigint,
    month        bigint,
    day          bigint,
    max_temp     double precision,
    min_temp     double precision,
    mean_temp    double precision,
    total_rain   double precision,
    total_snow   double precision,
    total_precip double precision,
    snow_on_grnd double precision
);

alter table sk_station_data
    owner to postgres;

create table soil_components
(
    poly_id           bigint,
    cmp               bigint,
    percent           bigint,
    slope             text,
    stone             text,
    surface_area      text,
    province          text,
    soil_code         text,
    modifier          text,
    profile           text,
    soil_id           text,
    coarse_frag_1     text,
    coarse_frag_2     text,
    depth             text,
    water_holding_cap text
);

alter table soil_components
    owner to postgres;

create table soil_data
(
    id                         text,
    province                   text,
    code                       text,
    modifier                   text,
    name                       text,
    kind                       text,
    water_table                text,
    root_restrict              text,
    restr_type                 text,
    drainage                   text,
    parent_material_texture_1  text,
    parent_material_texture_2  text,
    parent_material_texture_3  text,
    parent_material_chemical_1 text,
    parent_material_chemical_2 text,
    parent_material_chemical_3 text,
    mode_of_depo_1             text,
    mode_of_depo_2             text,
    mode_of_depo_3             text,
    layer_no                   bigint,
    u_depth                    bigint,
    l_depth                    bigint,
    hzn_lit                    text,
    hzn_mas                    text,
    hzn_suf                    text,
    hzn_mod                    text,
    percnt_coarse_frag         bigint,
    sand_texture               text,
    percnt_v_fine_sand         bigint,
    total_sand                 bigint,
    total_silt                 bigint,
    total_clay                 bigint,
    percnt_carbon              double precision,
    calcium_ph                 double precision,
    proj_ph                    double precision,
    percnt_base_sat            bigint,
    cec                        bigint,
    ksat                       double precision,
    water_reten_0              bigint,
    water_reten_10             bigint,
    water_reten_33             bigint,
    water_reten_1500           bigint,
    bulk_density               double precision,
    elec_cond                  bigint,
    calc_equiv                 bigint,
    decomp_class               bigint,
    percnt_wood                bigint
);

alter table soil_data
    owner to postgres;

create table soil_geometry
(
    area      double precision,
    perimeter double precision,
    poly_id   bigint,
    geometry  geometry(Polygon, 3347)
);

alter table soil_geometry
    owner to postgres;

create index idx_soil_geometry_geometry
    on soil_geometry using gist (geometry);

create table soil_moisture
(
    id            serial
        constraint pk_soil_moisture
            primary key,
    lon           double precision,
    lat           double precision,
    date          date,
    cr_num        integer,
    district      integer,
    soil_moisture double precision
);

alter table soil_moisture
    owner to "user";

create table soil_surronding_land
(
    poly_id    bigint,
    land_area  bigint,
    water_area bigint,
    fresh_area bigint,
    ocean_area bigint,
    total_area bigint
);

alter table soil_surronding_land
    owner to postgres;

create table station_data_last_updated
(
    station_id   varchar not null
        constraint pk_station_update
            primary key,
    last_updated date    not null,
    is_active    boolean default true
);

alter table station_data_last_updated
    owner to postgres;

create table stations_dly
(
    station_name   text,
    province       text,
    latitude       double precision,
    longitude      double precision,
    elevation      double precision,
    station_id     text,
    wmo_identifier double precision,
    tc_identifier  text,
    first_year     bigint,
    last_year      bigint,
    hly_first_year double precision,
    hly_last_year  double precision,
    dly_first_year double precision,
    dly_last_year  double precision,
    mly_first_year double precision,
    mly_last_year  double precision,
    geometry       geometry(Point, 3347),
    district       double precision,
    cr_num         double precision,
    scraped        boolean
);

alter table stations_dly
    owner to postgres;

create index idx_stations_dly_geometry
    on stations_dly using gist (geometry);

create table stations_hly
(
    station_name   text,
    province       text,
    latitude       double precision,
    longitude      double precision,
    elevation      double precision,
    station_id     text,
    wmo_identifier double precision,
    tc_identifier  text,
    first_year     bigint,
    last_year      bigint,
    hly_first_year double precision,
    hly_last_year  double precision,
    dly_first_year double precision,
    dly_last_year  double precision,
    mly_first_year double precision,
    mly_last_year  double precision,
    geometry       geometry(Point, 3347),
    district       double precision,
    cr_num         double precision,
    scraped        boolean
);

alter table stations_hly
    owner to postgres;

create index idx_stations_hly_geometry
    on stations_hly using gist (geometry);

