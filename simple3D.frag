uniform vec4 u_material_diffuse;

uniform vec4 u_material_specular;
uniform float u_shininess;

uniform vec4 u_material_ambient;

varying vec4 normal_normal;

const int u_NUM_OF_LIGHTS = 10;

varying vec4 lights_s[u_NUM_OF_LIGHTS];
varying vec4 lights_h[u_NUM_OF_LIGHTS];

uniform vec4 u_light_diffuses[u_NUM_OF_LIGHTS];
uniform vec4 u_light_speculars[u_NUM_OF_LIGHTS];
uniform vec4 u_light_ambients[u_NUM_OF_LIGHTS];

void main(void)
{
    vec4 color;
    float lambert;
    vec4 diffuse_color;
    float phong;
    vec4 specular_color;
    vec4 ambient_color;
    for(int i = 0; i < u_NUM_OF_LIGHTS; i++){
        // Diffuse
        lambert = max(dot(normalize(normal_normal), normalize(lights_s[i])), 0.0);
        diffuse_color = lambert * u_light_diffuses[i] * u_material_diffuse;

        // Specular
        phong = max(dot(normalize(normal_normal), normalize(lights_h[i])), 0.0);
        specular_color =  u_material_specular * u_light_speculars[i] * pow(phong, u_shininess);

        // Ambient
        ambient_color = u_light_ambients[i] * u_material_ambient;

        color += diffuse_color + specular_color + ambient_color;
    }


    gl_FragColor = color;
}