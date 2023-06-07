using System.Collections;
using UnityEngine;

public class TargetArea : MonoBehaviour
{
    public GameObject[] cubes;
    public float lightUpTime = 5.0f;
    
    void Start()
    {
        // The cubes array size will be 6, since you have 6 cubes.
        cubes = new GameObject[6];

        // Fetch each cube by name and store in the cubes array.
        for (int i = 0; i < 6   ; i++)
        {
            cubes[i] = transform.Find("Cube (" + i + ")").gameObject;
        }

        StartCoroutine(LightUpRandomCube());
    }

    IEnumerator LightUpRandomCube()
{
    while (true)
    {
        // Choose a random cube
        int randomIndex = Random.Range(0, cubes.Length);
        GameObject cube = cubes[randomIndex];

        // Light up the cube
        cube.GetComponent<Cube>().LightUp();

        // Wait for the light up time to pass
        yield return new WaitForSeconds(lightUpTime);

        // Turn off the light of the cube
        cube.GetComponent<Cube>().TurnOffLight();

        // Optionally, add a brief delay before the next cube lights up
        yield return new WaitForSeconds(0.5f);
    }
}

}
