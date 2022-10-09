
uniform vec4 u_light_diffuse;
uniform vec4 u_material_diffuse;


uniform vec4 u_light_specular;
uniform vec4 u_material_specular;
uniform float u_shininess;

uniform vec4 u_light_ambient;
uniform vec4 u_material_ambient;

varying vec4 s;
varying vec4 h;
varying vec4 normal_normal;

void main(void)
{
    // Diffuse
    float lambert = max(dot(normal_normal, s), 0.0);
	vec4 diffuse_color = lambert * u_light_diffuse * u_material_diffuse;

    // Specular
    float phong = max(dot(normal_normal, h), 0.0);
	vec4 specular_color = pow(phong, u_shininess) * u_light_specular * u_material_specular;

    // Ambient
    vec4 ambient_color = u_light_ambient * u_material_ambient;

    gl_FragColor = diffuse_color + specular_color + ambient_color;
}