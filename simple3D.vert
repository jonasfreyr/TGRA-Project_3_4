attribute vec3 a_position;
//## ADD CODE HERE ##

attribute vec3 a_normal;

uniform vec4 u_light_position;
uniform vec4 u_camera_position;

uniform mat4 u_model_matrix;
uniform mat4 u_projection_view_matrix;

uniform mat4 u_projection_matrix;
uniform mat4 u_view_matrix;

// uniform vec4 u_color;
// varying vec4 v_color;  //Leave the varying variables alone to begin with

varying vec4 s;
varying vec4 h;
varying vec4 normal_normal;

void main(void)
{
	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
	//## ADD CODE HERE ##
	vec4 normal = vec4(a_normal.x, a_normal.y, a_normal.z, 0.0);


	position = u_model_matrix * position;
	//## ADD CODE HERE ##
	normal = u_model_matrix * normal;

	// float light_factor_1 = max(dot(normalize(normal), normalize(vec4(1, 2, 3, 0))), 0.0);
	// float light_factor_2 = max(dot(normalize(normal), normalize(vec4(-3, -2, -1, 0))), 0.0);
	// v_color = (light_factor_1 + light_factor_2) * u_color; // ### --- Change this vector (pure white) to color variable --- #####

	normal_normal = normalize(normal);

	// Diffuse
	s = normalize(u_light_position - position);
	// float lambert = max(dot(normal_normal, normalize(s)), 0.0);
	// vec4 diffuse_color = lambert * u_light_diffuse * u_material_diffuse;

	// Specular
	vec4 v = normalize(u_camera_position - position);
	h = normalize(s + v);
	// float phong = max(dot(normal_normal, normalize(h)), 0.0);
	// vec4 specular_color = pow(phong, u_shininess) * u_light_specular * u_material_specular;

	// Ambient
	// vec4 ambient_color = u_light_ambient * u_material_ambient;

	// v_color = diffuse_color + specular_color + ambient_color;

	// ### --- Change the projection_view_matrix to separate view and projection matrices --- ### 
	position = u_view_matrix * position;
	position = u_projection_matrix * position;

	gl_Position = position;
}